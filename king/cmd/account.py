#!/usr/bin/env python
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

"""King Account Server.

This does the work of actually implementing the API calls made by the user.
Normal communications is done via the king API which then calls into this
account.
"""
import eventlet
import oslo_i18n as i18n
from king.common import config
from king.common import messaging
from king.common import profiler
from king import version
from king.rpc import api as rpc_api
from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr
from oslo_service import service


eventlet.monkey_patch()
i18n.enable_lazy()

LOG = logging.getLogger('king.account')


def main():
    # init king-account
    logging.register_options(cfg.CONF)
    cfg.CONF(project='king', prog='king-account',
             version=version.version_info.version_string())
    logging.setup(cfg.CONF, 'king-account')
    logging.set_defaults()
    messaging.setup()

    config.startup_sanity_check()

    from king.server import account as account  # noqa

    profiler.setup('king-account', cfg.CONF.host)
    gmr.TextGuruMeditation.setup_autorun(version)
    srv = account.AccountService(cfg.CONF.host, rpc_api.ACCOUNT_TOPIC)
    workers = cfg.CONF.num_account_workers
    if not workers:
        workers = max(1, processutils.get_worker_count())
    launcher = service.launch(cfg.CONF, srv, workers=workers)

    launcher.wait()
