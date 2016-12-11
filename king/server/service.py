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
import datetime
import eventlet
import oslo_messaging as messaging
import socket
import six
import uuid

from apscheduler.schedulers import background
from king.common import context
from king.rpc import api as rpc_api
from king.rpc import account_client as account_rpc_client
from king.objects import services as services_object
from king.objects import account as account_object
from king.objects import order as order_object
from king.objects import price as price_object

from king.clients.os import cinder
from king.clients.os import nova
from king.clients.os import glance
from king.clients.os import neutron

from king.common.i18n import _LE
from king.common.i18n import _LI
from king.common import messaging as rpc_messaging
from king.common import policy
from king.common import service_utils
from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service
from oslo_service import threadgroup
from oslo_utils import timeutils
from osprofiler import profiler


LOG = logging.getLogger(__name__)

RESOURCE_CLIENT = {
    'disk': cinder.BaseCinder(context.RequestContext()),
    'image': glance.BaseGlance(context.RequestContext()),
    'flavor': nova.BaseNova(context.RequestContext()),
    'instance': nova.BaseNova(context.RequestContext()),
    'floating-ip': neutron.BaseNeutron(context.RequestContext()),
}


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
            topic=rpc_api.SERVER_LISTENER_TOPIC)
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
        self.context = context.RequestContext()

        # The following are initialized here, but assigned in start() which
        # happens after the fork when spawning multiple worker processes
        self.listener = None
        self.worker_service = None
        self.engine_id = None
        self.thread_group_mgr = None
        self.target = None
        self.service_id = None
        self.manage_thread_grp = None
        self._rpc_server = None
        self.account_rpc_client = account_rpc_client.AccountClient()

        job_defaults = {
            'misfire_grace_time': 6048000,
            'coalesce': False,
            'max_instances': 24,
        }

        self.scheduler = background.BackgroundScheduler(
            job_defaults=job_defaults
        )
        self.order = order_object.Order()
        self.price = price_object.Price()
        self.account = account_object.Account()
        self.deduction_interval = cfg.CONF.deduction_interval

        self.resource_enforcer = policy.ResourceEnforcer()

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

        # if you have other resources, you may want to check the
        # status of that resource, like :
        # self.manage_thread_grp.add_thread(self.reset_stack_status)

        self.scheduler.start()
        self.inition_cron_task()
        super(EngineService, self).start()

    def _check_runnig_order_status(self, order):
        try:
            os_client = RESOURCE_CLIENT[order.order_type]
        except Exception as ex:
            LOG.error(ex)
            return False

        if order.order_type == 'disk':
            res = os_client.volume_get(order.resource_id)

        elif order.order_type == 'instance':
            res = os_client.get_server(order.resource_id)
            if res and res.status == 'SHUTOFF':
                return self.order.update_status(self.context,
                                                order.id,
                                                'STOP')
            if res and res.status == 'ERROR':
                return self.order.update_status(self.context,
                                                order.id,
                                                'STOP')

        elif order.order_type == 'floating_ip':
            res = os_client.get_flavor(order.resource_id)
        else:
            LOG.error("Error type of order: %s" % order.id)

        if res is None:
            return self.order.update_status(self.context,
                                            order.id,
                                            'DELETE')
        return order

    def _check_stop_order_status(self, order):
        try:
            os_client = RESOURCE_CLIENT[order.order_type]
        except Exception as ex:
            LOG.error(ex)
            return False

        if order.order_type == 'disk':
            res = os_client.volume_get(order.resource_id)

        elif order.order_type == 'instance':
            res = os_client.get_server(order.resource_id)
            if res and res.status == 'RUNNING':
                return self.order.update_status(self.context,
                                                order.id,
                                                'RUNNING')

        elif order.order_type == 'floating_ip':
            res = os_client.get_flavor(order.resource_id)
        else:
            LOG.error("Error type of order: %s" % order.id)

        if res is None:
            return self.order.update_status(self.context, order.id, 'DELETE')
        return order

    def _check_delete_order_status(self, order):
        try:
            os_client = RESOURCE_CLIENT[order.order_type]
        except Exception as ex:
            LOG.error(ex)
            return False

        if order.order_type == 'disk':
            res = os_client.volume_get(order.resource_id)

        elif order.order_type == 'instance':
            res = os_client.get_server(order.resource_id)
            if res and res.status == 'RUNNING':
                return self.order.update_status(self.context,
                                                order.id,
                                                'RUNNING')

        elif order.order_type == 'floating_ip':
            res = os_client.get_flavor(order.resource_id)
        else:
            LOG.error("Error type of order: %s" % order.id)

        if res:
            return self.order.update_status(self.context, order.id, 'RUNNING')
        return order

    def _check_order_status(self, order):
        LOG.debug("Interval: %s. Running Now." % self.deduction_interval)

        if order.order_status == 'RUNNING':
            return self._check_runnig_order_status(order)
        elif order.order_status == 'STOP':
            return self._check_stop_order_status(order)
        elif order.order_status == 'DELETE':
            return self._check_delete_order_status(order)
        else:
            LOG.error("Error status of order: %s" % order.id)
            return False

    def _from_db_get_all_order(self):
        return self.order.get_all(None)

    def inition_cron_task(self):
        LOG.debug("Interval: %s. Running Now." % self.deduction_interval)

        for order in self._from_db_get_all_order():
            order_check = self._check_order_status(order)
            if not order_check:
                continue
            if not order_check.order_status == 'RUNNING':
                continue
            self.cron_task(order_check)
            self.scheduler.add_job(self.cron_task,
                                   'interval',
                                   args=(order_check,),
                                   minutes=self.deduction_interval)
            LOG.debug("Deduction task of order: %s is Ready." % order.id)

    def count_pay(self, order):
        unit_price = self.price.get_by_id(None, order.price_id).price_num
        period_price = float(unit_price * self.deduction_interval)
        return period_price

    def cron_task(self, order):
        LOG.debug("Deduction task of %s Running." % order.id)
        pay_money = self.count_pay(order)
        self.account_rpc_client.account_pay_money(self.context,
                                                  order.project_id,
                                                  order.id,
                                                  pay_money)

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
        # ctxt = context.get_admin_context()

        # here should change the status of Service in databases
        # services_objects.Service.delete(ctxt, self.service_id)
        LOG.info(_LI('Service %s is deleted'), self.service_id)

        # Terminate the engine process
        LOG.info(_LI("All threads were gone, terminating engine"))
        super(EngineService, self).stop()

    def reset(self):
        super(EngineService, self).reset()
        logging.setup(cfg.CONF, 'king')

    @context.request_context
    def list_services(self, cnxt):
        result = {}
        services_list = [service_utils.format_service(srv)
                         for srv in services_object.Service.get_all(cnxt)]
        result['services'] = services_list
        return result

    @context.request_context
    def cron_create(self, cnxt, order_id):
        order = self.order.get(self.context, order_id=order_id)
        order_check = self._check_order_status(order)
        if not order_check:
            LOG.debug("Order check False :%s" % order.id)
            return False
        if not order_check.order_status == 'RUNNING':
            LOG.debug("Order status is Not RUNNING: %s" % order.id)
            return False
        self.cron_task(order_check)
        self.scheduler.add_job(self.cron_task,
                               'interval',
                               args=(order_check,),
                               minutes=self.deduction_interval)
        LOG.debug("Deduction task of order: %s is Ready." % order.id)

    def service_manage_report(self):
        cnxt = context.get_admin_context()

        if self.service_id is None:
            service_ref = services_object.Service.create(
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
            services_object.Service.update_by_id(cnxt,
                                                 self.service_id,
                                                 dict(deleted_at=None))
        except Exception as ex:
            LOG.error(_LE('Service %(service_id)s update '
                          'failed: %(error)s'),
                      {'service_id': self.service_id, 'error': ex})

    def service_manage_cleanup(self):
        cnxt = context.get_admin_context()
        last_window = (3 * cfg.CONF.periodic_interval)
        utcnow = timeutils.utcnow()
        last_update_time = utcnow - datetime.timedelta(seconds=last_window)

        service_refs = services_object.Service.get_all_by_args(cnxt,
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
                LOG.info("engine %s is dead." % service_ref['engine_id'])
                services_object.Service.delete(cnxt, service_ref['id'])
