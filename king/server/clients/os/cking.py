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

from keystoneclient import exceptions as ks_exceptions
from oslo_log import log as logging

from king.common import exception
from king.server.clients import client_plugin
from kingclient import client as kc

LOG = logging.getLogger(__name__)


CLIENT_NAME = 'king'
CLIENT_VERSION = '1'

class BaseKing(client_plugin.ClientPlugin):
    service_types = [QUOTA] = ['quota']


    def get_quota_api_version(self):
        '''Returns the most recent API version.'''
        endpoint_type = self._get_client_option(CLIENT_NAME, 'endpoint_type')
        try:
            self.url_for(service_type=self.QUOTA,
                         endpoint_type=endpoint_type)
            return 1
        except ks_exceptions.EndpointNotFound:
            return None


    def authenticated_client(self):
        con = self.context

        # define api version
        quota_api_version = self.get_quota_api_version()
        if quota_api_version == 1:
            service_type = self.QUOTA
            client_version = '1'

        # get endpoint_type
        endpoint_type = self._get_client_option(CLIENT_NAME, 'endpoint_type')
        endpoint_url = self.get_king_url()

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
            'endpoint': endpoint_url,
            'token' : self.auth_token,
            'cacert': None,
            'insecure': None,
            'extensions': None
        }

        client = kc.Client(CLIENT_VERSION, **args)
        return client


    def get_king_url(self):
        king_url = self._get_client_option(CLIENT_NAME, 'url')
        if king_url:
            tenant_id = self.context.tenant_id
            king_url = king_url % {'tenant_id': tenant_id}
        else:
            endpoint_type = self._get_client_option(CLIENT_NAME,
                                                    'endpoint_type')
            king_url = self.url_for(service_type=self.QUOTA,
                                    endpoint_type=endpoint_type)
        return king_url


    def get_volume_info(self):
        volumes = self.client.volumes.list()
        size = 0
        for volume in volumes:
            size += volume.size
        volume_info = {
            'volume_size':size,
            'volume_num':len(volumes),
        }
        return volume_info

    def check_volumes_quotas(self, body):
        kclient = self.authenticated_client()
        quota = kclient.quota.show(self.context.user_id)
    
        # check volume quotas
        volume_quota = quota['volume'][0]
        volume_info = self.get_volume_info()
        if int(volume_quota.volume_size) < volume_info['volume_size'] + body['size'] \
            or int(volume_quota.volume_num) < volume_info['volume_num'] + 1:
            return False
        return True
