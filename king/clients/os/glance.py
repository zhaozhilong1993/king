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

from glanceclient import client as gc
from novaclient import client as nc
from oslo_log import log as logging

from king.clients import client_plugin

LOG = logging.getLogger(__name__)

CLIENT_NAME = 'glance'
CLIENT_VERSION = '2'


class BaseGlance(client_plugin.ClientPlugin):

    def authenticated_glance_client(self):
        # get glance endpoint
        client = gc.Client(CLIENT_VERSION, session=self.sess)
        return client

    def authenticated_nova_client(self):
        # get nova endpoint
        client = nc.Client(CLIENT_VERSION, session=self.sess)
        return client

    def get_image(self, image_id):
        nc = self.authenticated_nova_client()
        try:
            res = nc.images.get(image_id)
        except Exception as ex:
            res = None
            LOG.error("Image resource error: %s" % ex)
        return res
