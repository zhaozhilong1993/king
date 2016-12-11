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
from king.clients import client_plugin

LOG = logging.getLogger(__name__)

PAY_ROLE_NAME = 'payer'
CLIENT_NAME = 'keystone'
CLIENT_VERSION = '3'


class BaseKeystone(client_plugin.ClientPlugin):

    def authenticated_client(self):
        # get keystone endpoint
        client = kc.Client(session=self.sess)
        return client

    def get_payer_id(self, project_id):
        kc = self.authenticated_client()
        payer_role = kc.roles.list(name=PAY_ROLE_NAME)
        LOG.debug("Search the payer of project: %s" % project_id)

        if not payer_role:
            LOG.error("Keystone Role: %s Not found." % PAY_ROLE_NAME)
            raise exception.RolePayerNotFound()

        payer = kc.role_assignments.list(project=project_id,
                                         role=payer_role[0])
        if not payer:
            LOG.error("Project: %s Not found a payer." % project_id)
            raise exception.ProjectPayerNotFound(project_id)
        return payer[0].user['id']
