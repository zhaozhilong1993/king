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

from keystoneclient.v3 import client as kc
from oslo_log import log as logging

from king.common import exception
from king.common.i18n import _LI
from king.clients import client_plugin

LOG = logging.getLogger(__name__)

PAY_ROLE_NAME = 'payer'
CLIENT_NAME = 'keystone'
CLIENT_VERSION = '3'


class BaseKeystone(client_plugin.ClientPlugin):
    service_types = [IDENTITY] = ['identity']

    def get_keystone_url(self):
        keystone_url = self._get_client_option(CLIENT_NAME, 'auth_uri')
        if keystone_url:
            tenant_id = self.context.tenant_id
            keystone_url = keystone_url % {'tenant_id': tenant_id}
        else:
            endpoint_type = self._get_client_option(CLIENT_NAME,
                                                    'endpoint_type')
            keystone_url = self.url_for(service_type=self.IDENTITY,
                                        endpoint_type=endpoint_type)
        return keystone_url

    def authenticated_client(self):
        # get keystone endpoint
        client = kc.Client(session=self.sess)
        return client

    def get_payer_id(self, project_id):
        kc = self.authenticated_client()
        payer_role = kc.roles.list(name=PAY_ROLE_NAME)

        if not payer_role:
            LOG.error(_LI("Keystone Role: %s Not found." % PAY_ROLE_NAME))
            raise exception.RolePayerNotFound()

        payer = kc.role_assignments.list(project=project_id,
                                         role=payer_role[0])
        if not payer:
            LOG.error(_LI("Project: %s Not found a payer." % project_id))
            raise exception.ProjectPayerNotFound()
        return payer[0].user['id']
