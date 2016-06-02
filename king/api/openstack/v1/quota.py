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
from king.rpc import api as rpc_api
from king.rpc import client as rpc_client


LOG = logging.getLogger(__name__)


class QuotaController(object):
    """WSGI controller for stacks resource in King v1 API.

    Implements the API actions.
    """
    # Define request scope (must match what is in policy.json)
    REQUEST_SCOPE = 'quota'

    def __init__(self, options):
        self.options = options
        self.rpc_client = rpc_client.EngineClient()

    @util.policy_enforce
    def list(self, req):
        """get all quota"""
        res = self.rpc_client.list_quota(
        req.context,
        )
        return res


    @util.policy_enforce
    def list_default(self, req):
        """get all quota"""
        res = self.rpc_client.list_default_quota(
        req.context,
        )
        return res

def create_resource(options):
    """Stacks resource factory method."""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = serializers.JSONResponseSerializer()
    return wsgi.Resource(QuotaController(options), deserializer, serializer)
