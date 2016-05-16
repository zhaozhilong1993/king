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

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
import osprofiler.profiler
import osprofiler.web

from king.common import context
from king.common.i18n import _LW
from king.common import messaging as rpc_messaging

cfg.CONF.import_opt('enabled', 'king.common.config', group='profiler')

LOG = logging.getLogger(__name__)


def setup(binary, host):
    if cfg.CONF.profiler.enabled:
        _notifier = osprofiler.notifier.create(
            "Messaging", messaging, context.get_admin_context().to_dict(),
            rpc_messaging.TRANSPORT, "king", binary, host)
        osprofiler.notifier.set(_notifier)
        osprofiler.web.enable(cfg.CONF.profiler.hmac_keys)
        LOG.warning(_LW("OSProfiler is enabled.\nIt means that person who "
                        "knows any of hmac_keys that are specified in "
                        "/etc/king/king.conf can trace his requests. \n"
                        "In real life only operator can read this file so "
                        "there is no security issue. Note that even if person "
                        "can trigger profiler, only admin user can retrieve "
                        "trace information.\n"
                        "To disable OSprofiler set in king.conf:\n"
                        "[profiler]\nprofiler_enabled=false"))
    else:
        osprofiler.web.disable()
