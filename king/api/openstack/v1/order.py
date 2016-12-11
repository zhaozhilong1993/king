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

"""order endpoint for King v1 REST API."""
import json
import six
from webob import exc

from king.api.openstack.v1 import util
from king.common import serializers
from king.common import service_utils
from king.common import wsgi

from king.common.i18n import _

from king.objects.order import Order as order_object

from king.rpc import server_client as server_rpc_client
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class OrderController(object):
    """WSGI controller for order resource in King v1 API.

    Implements the API actions.
    """
    # Define request scope (must match what is in policy.json)
    REQUEST_SCOPE = 'order'

    def __init__(self, options):
        self.options = options
        self.server_client = server_rpc_client.ServerClient()

    @util.policy_enforce
    def list(self, req):
        """get all order"""
        pass

    @util.policy_enforce
    def show(self, req):
        """get all order"""
        pass

    @util.policy_enforce
    def create(self, req, body):
        """create order"""
        body_str = req.body
        try:
            body = json.loads(body_str)
        except ValueError as ex:
            msg = _("Post data error: %s") % ex
            raise exc.HTTPBadRequest(six.text_type(msg))

        if 'order' in body:
            try:
                if body['order']['resource_id'] is None:
                    msg = _("Post data error: resource_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
                if body['order']['price_id'] is None:
                    msg = _("Post data error: price_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
                if body['order']['project_id'] is None:
                    msg = _("Post data error: project_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
            except KeyError as ex:
                    msg = _("Post data error: some key not be found")
                    raise exc.HTTPBadRequest(six.text_type(msg))
            res = service_utils.to_dict(order_object.create(req.context,
                                                            body['order']))
            self.server_client.cron_create(req.context, res['id'])
            return res
        else:
            msg = _("Post data error: key order not found")
            raise exc.HTTPBadRequest(six.text_type(msg))

    @util.policy_enforce
    def update_status(self, req):
        """update order"""
        body_str = req.body
        try:
            body = json.loads(body_str)
        except ValueError as ex:
            msg = _("Post data error: %s") % ex
            raise exc.HTTPBadRequest(six.text_type(msg))

        if 'order' in body:
            msg = _("Post data error: key order not found")
            raise exc.HTTPBadRequest(six.text_type(msg))
        else:
            try:
                if body['order']['resource_id'] is None:
                    msg = _("Post data error: resource_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
            except KeyError as ex:
                msg = _("Post data error: some key not be found")
                raise exc.HTTPBadRequest(six.text_type(msg))
        pass


def create_resource(options):
    """order resource factory method."""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = serializers.JSONResponseSerializer()
    return wsgi.Resource(OrderController(options), deserializer, serializer)
