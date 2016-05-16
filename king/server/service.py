#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import uuid
import socket

import eventlet
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_service import service
from oslo_service import threadgroup
from oslo_utils import timeutils
from osprofiler import profiler
import six
import datetime

from king.common import context
from king.objects import service as service_object

from king.common.i18n import _LE
from king.common.i18n import _LI
from king.common.i18n import _LW
from king.common import messaging as rpc_messaging
from king.common import policy


from king.rpc import api as rpc_api




LOG = logging.getLogger(__name__)


class ThreadGroupManager(object):

    def __init__(self):
        super(ThreadGroupManager, self).__init__()
        self.groups = {}
        self.events = collections.defaultdict(list)

        # Create dummy service task, because when there is nothing queued
        # on self.tg the process exits
        self.add_timer(cfg.CONF.periodic_interval, self._service_task)

    def _service_task(self):
        """Dummy task which gets queued on the service.Service threadgroup.

        Without this, service.Service sees nothing running i.e has nothing to
        wait() on, so the process exits. This could also be used to trigger
        periodic non-stack-specific housekeeping tasks.
        """
        pass

    def _serialize_profile_info(self):
        prof = profiler.get()
        trace_info = None
        if prof:
            trace_info = {
                "hmac_key": prof.hmac_key,
                "base_id": prof.get_base_id(),
                "parent_id": prof.get_id()
            }
        return trace_info

    def _start_with_trace(self, trace, func, *args, **kwargs):
        if trace:
            profiler.init(**trace)
        return func(*args, **kwargs)

    def start(self, stack_id, func, *args, **kwargs):
        """Run the given method in a sub-thread."""
        if stack_id not in self.groups:
            self.groups[stack_id] = threadgroup.ThreadGroup()

        def log_exceptions(gt):
            try:
                gt.wait()
            except Exception:
                LOG.exception(_LE('Unhandled error in asynchronous task'))
            except BaseException:
                pass

        th = self.groups[stack_id].add_thread(self._start_with_trace,
                                              self._serialize_profile_info(),
                                              func, *args, **kwargs)
        th.link(log_exceptions)
        return th



    def start_with_acquired_lock(self, stack, lock, func, *args, **kwargs):
        """Run the given method in a sub-thread with an existing stack lock.

        Release the provided lock when the thread finishes.

        :param stack: Stack to be operated on
        :type stack: king.engine.parser.Stack
        :param lock: The acquired stack lock
        :type lock: king.engine.stack_lock.StackLock
        :param func: Callable to be invoked in sub-thread
        :type func: function or instancemethod
        :param args: Args to be passed to func
        :param kwargs: Keyword-args to be passed to func

        """
        def release(gt):
            """Callback function that will be passed to GreenThread.link().

            Persist the stack state to COMPLETE and FAILED close to
            releasing the lock to avoid race condtitions.
            """
            if stack is not None and stack.action not in (
                    stack.DELETE, stack.ROLLBACK, stack.UPDATE):
                stack.persist_state_and_release_lock(lock.engine_id)
            else:
                lock.release()

        # Link to self to allow the stack to run tasks
        stack.thread_group_mgr = self
        th = self.start(stack.id, func, *args, **kwargs)
        th.link(release)
        return th

    def add_timer(self, stack_id, func, *args, **kwargs):
        """Define a periodic task in the stack threadgroups.

        The task is run in a separate greenthread.

        Periodicity is cfg.CONF.periodic_interval
        """
        if stack_id not in self.groups:
            self.groups[stack_id] = threadgroup.ThreadGroup()
        self.groups[stack_id].add_timer(cfg.CONF.periodic_interval,
                                        func, *args, **kwargs)

    def add_event(self, stack_id, event):
        self.events[stack_id].append(event)

    def remove_event(self, gt, stack_id, event):
        for e in self.events.pop(stack_id, []):
            if e is not event:
                self.add_event(stack_id, e)

    def stop_timers(self, stack_id):
        if stack_id in self.groups:
            self.groups[stack_id].stop_timers()

    def stop(self, stack_id, graceful=False):
        """Stop any active threads on a stack."""
        if stack_id in self.groups:
            self.events.pop(stack_id, None)
            threadgroup = self.groups.pop(stack_id)
            threads = threadgroup.threads[:]

            threadgroup.stop(graceful)
            threadgroup.wait()

            # Wait for link()ed functions (i.e. lock release)
            links_done = dict((th, False) for th in threads)

            def mark_done(gt, th):
                links_done[th] = True

            for th in threads:
                th.link(mark_done, th)
            while not all(six.itervalues(links_done)):
                eventlet.sleep()

    def send(self, stack_id, message):
        for event in self.events.pop(stack_id, []):
            event.send(message)


@profiler.trace_cls("rpc")
class EngineListener(service.Service):
    """Listen on an AMQP queue named for the engine.

    Allows individual engines to communicate with each other for multi-engine
    support.
    """

    ACTIONS = (STOP_STACK, SEND) = ('stop_stack', 'send')

    def __init__(self, host, engine_id, thread_group_mgr):
        super(EngineListener, self).__init__()
        self.thread_group_mgr = thread_group_mgr
        self.engine_id = engine_id
        self.host = host

    def start(self):
        super(EngineListener, self).start()
        self.target = messaging.Target(
            server=self.engine_id,
            topic=rpc_api.LISTENER_TOPIC)
        server = rpc_messaging.get_rpc_server(self.target, self)
        server.start()

    def listening(self, ctxt):
        """Respond to a watchdog request.

        Respond affirmatively to confirm that the engine performing the action
        is still alive.
        """
        return True

    def stop_stack(self, ctxt, stack_identity):
        """Stop any active threads on a stack."""
        stack_id = stack_identity['stack_id']
        self.thread_group_mgr.stop(stack_id)

    def send(self, ctxt, stack_identity, message):
        stack_id = stack_identity['stack_id']
        self.thread_group_mgr.send(stack_id, message)


@profiler.trace_cls("rpc")
class EngineService(service.Service):
    """Manages the running instances from creation to destruction.

    All the methods in here are called from the RPC backend.  This is
    all done dynamically so if a call is made via RPC that does not
    have a corresponding method here, an exception will be thrown when
    it attempts to call into this class.  Arguments to these methods
    are also dynamically added and will be named as keyword arguments
    by the RPC caller.
    """

    RPC_API_VERSION = '1.0'

    def __init__(self, host, topic):
        super(EngineService, self).__init__()

        self.host = host
        self.topic = topic
        self.process = 'king-server'
        self.hostname = socket.gethostname()

        # The following are initialized here, but assigned in start() which
        # happens after the fork when spawning multiple worker processes
        self.stack_watch = None
        self.listener = None
        self.worker_service = None
        self.engine_id = None
        self.thread_group_mgr = None
        self.target = None
        self.service_id = None
        self.manage_thread_grp = None
        self._rpc_server = None

        self.resource_enforcer = policy.ResourceEnforcer()

        if cfg.CONF.trusts_delegated_roles:
            LOG.warning(_LW('The default value of "trusts_delegated_roles" '
                            'option in king.conf is changed to [] in Kilo '
                            'and king will delegate all roles of trustor. '
                            'Please keep the same if you do not want to '
                            'delegate subset roles when upgrading.'))

    def start(self):
        # engine_id is used to label this engine
        self.engine_id = str(uuid.uuid4())

        if self.thread_group_mgr is None:
            self.thread_group_mgr = ThreadGroupManager()
        # start rpc listen from other engine
        self.listener = EngineListener(self.host, self.engine_id,
                                       self.thread_group_mgr)
        LOG.debug("Starting listener for engine %s" % self.engine_id)
        self.listener.start()

        # start rpc listen from other openstack part
        target = messaging.Target(
            version=self.RPC_API_VERSION, server=self.host,
            topic=self.topic)
        self.target = target

        # rpc_messaging is rewrite by us,
        # target is still mean target, self is mean endpoint
        # the function is in common
        self._rpc_server = rpc_messaging.get_rpc_server(target, self)
        self._rpc_server.start()
        self._client = rpc_messaging.get_rpc_client(
            version=self.RPC_API_VERSION)

        # may be you will want to init your service manager here
        self.service_manage_cleanup()

        if self.manage_thread_grp is None:
            self.manage_thread_grp = threadgroup.ThreadGroup()

        # here is to recheck service alive
        # like
        self.manage_thread_grp.add_timer(cfg.CONF.periodic_interval,
                                         self.service_manage_report)

        # if you have other resources , you may want to check the status of that resources
        # like :
        # self.manage_thread_grp.add_thread(self.reset_stack_status)

        super(EngineService, self).start()

    def _stop_rpc_server(self):
        # Stop rpc connection at first for preventing new requests
        LOG.debug("Attempting to stop engine service...")
        try:
            self._rpc_server.stop()
            self._rpc_server.wait()
            LOG.info(_LI("Engine service is stopped successfully"))
        except Exception as e:
            LOG.error(_LE("Failed to stop engine service, %s"), e)

    def stop(self):
        self._stop_rpc_server()

        if cfg.CONF.convergence_engine:
            # Stop the WorkerService
            self.worker_service.stop()

        # Wait for all active threads to be finished
        for stack_id in list(self.thread_group_mgr.groups.keys()):
            # Ignore dummy service task
            if stack_id == cfg.CONF.periodic_interval:
                continue
            LOG.info(_LI("Waiting stack %s processing to be finished"),
                     stack_id)
            # Stop threads gracefully
            self.thread_group_mgr.stop(stack_id, True)
            LOG.info(_LI("Stack %s processing was finished"), stack_id)

        self.manage_thread_grp.stop()
        ctxt = context.get_admin_context()

        # here should change the status of Service in databases
        # service_objects.Service.delete(ctxt, self.service_id)
        LOG.info(_LI('Service %s is deleted'), self.service_id)

        # Terminate the engine process
        LOG.info(_LI("All threads were gone, terminating engine"))
        super(EngineService, self).stop()

    def reset(self):
        super(EngineService, self).reset()
        logging.setup(cfg.CONF, 'king')
        
    def service_manage_report(self):
        cnxt = context.get_admin_context()

        if self.service_id is None:
            service_ref = service_object.Service.create(
                cnxt,
                values={
                    'host': self.host,
                    'hostname': self.hostname,
                    'process': self.process,
                    'engine_id': self.engine_id,
                    'topic': self.topic,
                    'report_interval': cfg.CONF.periodic_interval
                }
            )
            self.service_id = service_ref['id']
            LOG.info("service engine %s is start" % service_ref['engine_id'])

        try:
            # update the service info, cause will use in service_manage_cleanup
            service_object.Service.update_by_id(cnxt,
                                                service_ref['id'],
                                                dict(deleted_at=None))
        except Exception as ex:
            LOG.error(_LE('Service %(service_id)s update '
                          'failed: %(error)s'),
                      {'service_id': self.service_id, 'error': ex})



    def service_manage_cleanup(self):
        cnxt = context.get_admin_context()
        last_update_window = (3 * cfg.CONF.periodic_interval)
        last_update_time = timeutils.utcnow() - datetime.timedelta(seconds=last_update_window)

        service_refs = service_object.Service.get_all_by_args(cnxt,
                                                              self.host,
                                                              self.process,
                                                              self.hostname)
        for service_ref in service_refs:
            # means the process is deleted by others
            if (service_ref['updated_at'] is None
                or service_ref['deleted_at'] is not None):
                continue
            if service_ref['updated_at'] < last_update_time:
                # maybe service is dead
                LOG.info("service engine %s is dead or in some bad status"% service_ref['engine_id'])
                service_object.Service.delete(cnxt, service_ref['id'])
