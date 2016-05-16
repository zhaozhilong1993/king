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

"""Stack endpoint for King v1 REST API."""

from oslo_log import log as logging

from king.api.openstack.v1 import util
from king.common import serializers
from king.common import wsgi

from king.db import api as db_api

LOG = logging.getLogger(__name__)


class UserController(object):
    """WSGI controller for stacks resource in King v1 API.

    Implements the API actions.
    """
    # Define request scope (must match what is in policy.json)
    REQUEST_SCOPE = 'users'

    def __init__(self, options):
        self.options = options
        self.rpc_client = None

    @util.policy_enforce
    def list(self, req):
        """get all use"""
        res = db_api.db_get_user(req.context, 'demo')
        return res


    @util.policy_enforce
    def create(self, req):
        """create a user"""
        import pdb
        pdb.set_trace()
        user = {
            'user_name': 'demo',
            'user_email': 'test@email.com'
        }

        res = db_api.db_add_user(req.context, user)
        return res


def create_resource(options):
    """Stacks resource factory method."""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = serializers.JSONResponseSerializer()
    return wsgi.Resource(UserController(options), deserializer, serializer)
