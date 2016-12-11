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

from novaclient import client as nc
from oslo_log import log as logging

from king.clients import client_plugin

LOG = logging.getLogger(__name__)

CLIENT_NAME = 'nova'
CLIENT_VERSION = '2.1'


class BaseNova(client_plugin.ClientPlugin):

    def authenticated_client(self):
        # get nova endpoint
        client = nc.Client(CLIENT_VERSION, session=self.sess)
        return client

    def get_flavor(self, flavor_id):
        client = self.authenticated_client()
        try:
            res = client.flavors.get(flavor_id)
        except Exception as ex:
            res = None
            LOG.error("Flavor resource error: %s" % ex)
        return res
