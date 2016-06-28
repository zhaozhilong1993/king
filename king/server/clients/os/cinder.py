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

from cinderclient import client as cc
from cinderclient import exceptions
from keystoneclient import exceptions as ks_exceptions
from oslo_log import log as logging

from king.common import exception
from king.server.clients import client_plugin
from king.server.clients.os.cking import BaseKing as cking

LOG = logging.getLogger(__name__)

CLIENT_NAME = 'cinder'
CLIENT_VERSION = '1'

class BaseCinder(client_plugin.ClientPlugin):
    service_types = [VOLUME, VOLUME_V2] = ['volume', 'volumev2']


    def get_volume_api_version(self):
        '''Returns the most recent API version.'''

        endpoint_type = self._get_client_option(CLIENT_NAME, 'endpoint_type')
        try:
            self.url_for(service_type=self.VOLUME_V2,
                         endpoint_type=endpoint_type)
            return 2
        except ks_exceptions.EndpointNotFound:
            try:
                self.url_for(service_type=self.VOLUME,
                             endpoint_type=endpoint_type)
                return 1
            except ks_exceptions.EndpointNotFound:
                return None


    def authenticated_client(self):
        con = self.context

        # define api version
        volume_api_version = self.get_volume_api_version()
        if volume_api_version == 1:
            service_type = self.VOLUME
            client_version = '1'
        elif volume_api_version == 2:
            service_type = self.VOLUME_V2
            client_version = '2'

        # get endpoint_type
        endpoint_type = self._get_client_option(CLIENT_NAME, 'endpoint_type')

        # get cinder endpoint
        management_url = self.url_for(service_type=service_type,
                                      endpoint_type=endpoint_type)

        args = {
            'service_type': service_type,
            'auth_url': con.auth_url or '',
            'project_id': con.tenant_id,
            'username': None,
            'api_key': None,
            'endpoint_type': endpoint_type,
            'cacert': None,
            'insecure': None,
            'extensions': None
        }

        client = cc.Client(CLIENT_VERSION, **args)
        client.client.auth_token = self.auth_token
        client.client.management_url = management_url
        client.volume_api_version = volume_api_version
        return client


    def create_volume(self, body):
        cclient = self.authenticated_client()
        # inition king
        self.king = cking(self.context, client=cclient)

        if self.king.check_volumes_quotas(body) is False:
            raise exception.QuotaNotEnough('volume')
        res = cclient.volumes.create(**body)
        return res
