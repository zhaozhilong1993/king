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

"""king API Server.

An OpenStack ReST API to king.
"""
import eventlet
import sys
import six
import oslo_i18n as i18n
from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr
from oslo_service import systemd
from king.common import config
from king.common.i18n import _LI
from king.common import messaging
from king.common import profiler
from king.common import wsgi
from king import version

eventlet.monkey_patch(os=False)
i18n.enable_lazy()

LOG = logging.getLogger('king.api')


def main():
    try:
        logging.register_options(cfg.CONF)
        cfg.CONF(project='king', prog='king-api',
                 version=version.version_info.version_string())
        logging.setup(cfg.CONF, 'king-api')
        messaging.setup()

        app = config.load_paste_app()

        port = cfg.CONF.king_api.bind_port
        host = cfg.CONF.king_api.bind_host
        LOG.info(_LI('Starting King REST API on %(host)s:%(port)s'),
                 {'host': host, 'port': port})
        profiler.setup('king-api', host)
        gmr.TextGuruMeditation.setup_autorun(version)
        server = wsgi.Server('king-api', cfg.CONF.king_api)
        server.start(app, default_port=port)
        systemd.notify_once()
        server.wait()
    except RuntimeError as e:
        msg = six.text_type(e)
        sys.exit("ERROR: %s" % msg)
