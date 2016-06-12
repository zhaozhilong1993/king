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

"""quota endpoint for King v1 REST API."""

from oslo_log import log as logging
from webob import exc
import six
import json

from king.api.openstack.v1 import util
from king.common import serializers
from king.common import wsgi

from king.db import api as db_api
from king.rpc import api as rpc_api
from king.rpc import client as rpc_client

from king.common.i18n import _

LOG = logging.getLogger(__name__)


class VolumeController(object):
    """WSGI controller for volume resource in King v1 API.

    Implements the API actions.
    """
    # Define request scope (must match what is in policy.json)
    REQUEST_SCOPE = 'volume'

    def __init__(self, options):
        self.options = options
        self.rpc_client = rpc_client.EngineClient()

    @util.policy_enforce
    def create(self, req):
        """create cinder volume"""
        body_str = req.body
        try:
            body = json.loads(body_str)
        except ValueError as ex:
            msg = _("Post data is not supported: %s") % ex
            raise exc.HTTPBadRequest(six.text_type(msg))

        if not body.has_key('volume'):
            msg = _("Post data is not supported: key volume not found")
            raise exc.HTTPBadRequest(six.text_type(msg))
        else :
            try:
                if body['volume']['size'] is None:
                    msg = _("Post data is not supported: key volume size can not be None")
                    raise exc.HTTPBadRequest(six.text_type(msg))
            except KeyError as ex:
                msg = _("Post data is not supported: key volume size can not be found")
                raise exc.HTTPBadRequest(six.text_type(msg))

        res = self.rpc_client.create_volume(req.context,
                                            body)
        return res


def create_resource(options):
    """volume resource factory method."""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = serializers.JSONResponseSerializer()
    return wsgi.Resource(VolumeController(options), deserializer, serializer)
