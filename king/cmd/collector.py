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

"""Heat Engine Server.

This does the work of actually implementing the API calls made by the user.
Normal communications is done via the king API which then calls into this
engine.
"""

import eventlet
eventlet.monkey_patch()

from oslo_concurrency import processutils
from oslo_config import cfg
import oslo_i18n as i18n
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr
from oslo_service import service

from king.common import config
from king.rpc import api as rpc_api
from king.common import messaging
from king.common import profiler

from king import version

i18n.enable_lazy()

LOG = logging.getLogger('king.collector')


def main():
    # init engine
    logging.register_options(cfg.CONF)
    cfg.CONF(project='king', prog='king-collector',
             version=version.version_info.version_string())
    logging.setup(cfg.CONF, 'king-collector')
    logging.set_defaults()
    messaging.setup()

    config.startup_sanity_check()

    from king.server import collector

    profiler.setup('king-collector', cfg.CONF.host)
    gmr.TextGuruMeditation.setup_autorun(version)
    srv = collector.CollectorService(cfg.CONF.host, rpc_api.COLLECTOR_TOPIC)
    workers = cfg.CONF.num_engine_workers
    if not workers:
        workers = max(4, processutils.get_worker_count())

    launcher = service.launch(cfg.CONF, srv, workers=workers)

    launcher.wait()
