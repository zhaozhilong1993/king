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

from neutronclient.v2_0 import client as nc
from oslo_log import log as logging

from king.clients import client_plugin

CLIENT_NAME = 'neutron'
LOG = logging.getLogger(__name__)


class BaseNeutron(client_plugin.ClientPlugin):

    def authenticated_client(self):
        # get neutron endpoint
        client = nc.Client(session=self.sess)
        return client

    def get_floating_ip(self, floating_ip):
        nc = self.authenticated_client()
        try:
            res = nc.show_floatingip(floating_ip)
        except Exception as ex:
            res = None
            LOG.error("Floating ip resource error: %s" % ex)
        return res
