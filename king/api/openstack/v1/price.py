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

"""price endpoint for King v1 REST API."""
import json
import six
from webob import exc

from oslo_log import log as logging

from king.common.i18n import _

from king.api.openstack.v1 import util
from king.common import serializers
from king.common import service_utils
from king.common import wsgi

from king.objects.price import Price as price_object


LOG = logging.getLogger(__name__)


class PriceController(object):
    """WSGI controller for price resource in King v1 API.

    Implements the API actions.
    """
    # Define request scope (must match what is in policy.json)
    REQUEST_SCOPE = 'price'

    def __init__(self, options):
        self.options = options

    @util.policy_enforce
    def list(self, req):
        """get all price"""
        pass

    @util.policy_enforce
    def show(self, req, body):
        """get all price"""
        pass

    @util.policy_enforce
    def create(self, req, body):
        """create price"""
        body_str = req.body
        try:
            body = json.loads(body_str)
        except ValueError as ex:
            msg = _("Post data error: %s") % ex
            raise exc.HTTPBadRequest(six.text_type(msg))
        if 'price' in body:
            try:
                if body['price']['order_type'] is None:
                    msg = _("Post data error: order_type can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
                if body['price']['price_num'] is None:
                    msg = _("Post data error: price_num can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
            except KeyError as ex:
                msg = _("Post data error: some key not be found")
                raise exc.HTTPBadRequest(six.text_type(msg))
            # create price template
            if body['price']['resource_type'] == 'disk' or \
                    body['price']['resource_type'] == 'floating_ip':
                body['price']['resource_id'] = 'UNUSE'
            return service_utils.to_dict(price_object.create(req.context,
                                                             body['price']))
        else:
            msg = _("Post data error: key order not found")
            raise exc.HTTPBadRequest(six.text_type(msg))

    @util.policy_enforce
    def update_status(self, req):
        """create price"""
        pass


def create_resource(options):
    """price resource factory method."""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = serializers.JSONResponseSerializer()
    return wsgi.Resource(PriceController(options), deserializer, serializer)
