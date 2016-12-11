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

from cinderclient.v1 import client as cc
from oslo_log import log as logging

from king.clients import client_plugin

LOG = logging.getLogger(__name__)

CLIENT_NAME = 'cinder'


class BaseCinder(client_plugin.ClientPlugin):

    def authenticated_client(self):
        # get cinder endpoint
        client = cc.Client(session=self.sess)
        return client

    def volume_get(self, volume_id):
        cc = self.authenticated_client()
        try:
            res = cc.volumes.get(volume_id)
        except Exception as ex:
            res = None
            LOG.error("Volume resource error: %s" % ex)
        return res
