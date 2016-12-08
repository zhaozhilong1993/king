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

"""action endpoint for King v1 REST API."""
import json
import six
from webob import exc

from king.api.openstack.v1 import util
from king.common import serializers
from king.common import service_utils
from king.common import wsgi

from king.common.i18n import _

from king.objects.action import Action as action_object

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class ActionController(object):
    """WSGI controller for action resource in King v1 API.

    Implements the API actions.
    """
    # Define request scope (must match what is in policy.json)
    REQUEST_SCOPE = 'action'

    def __init__(self, options):
        self.options = options

    @util.policy_enforce
    def list(self, req):
        """get all action"""
        pass

    @util.policy_enforce
    def show(self, req):
        """get all action"""
        pass

    @util.policy_enforce
    def create(self, req, body):
        """create action"""
        body_str = req.body
        try:
            body = json.loads(body_str)
        except ValueError as ex:
            msg = _("Post data error: %s") % ex
            raise exc.HTTPBadRequest(six.text_type(msg))
        if 'action' in body:
            try:
                if body['action']['resource_id'] is None:
                    msg = _("Post data error: resource_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
                if body['action']['resource_type'] is None:
                    msg = _("Post data error: resource_type can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
                if body['action']['project_id'] is None:
                    msg = _("Post data error: project_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
                if body['action']['user_id'] is None:
                    msg = _("Post data error: user_id can not be null")
                    raise exc.HTTPBadRequest(six.text_type(msg))
            except KeyError as ex:
                msg = _("Post data error: some key not be found")
                raise exc.HTTPBadRequest(six.text_type(msg))
            # create action record
            return service_utils.to_dict(action_object.create(req.context,
                                                              body['action']))
        else:
            msg = _("Post data error: key order not found")
            raise exc.HTTPBadRequest(six.text_type(msg))


def create_resource(options):
    """action resource factory method."""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = serializers.JSONResponseSerializer()
    return wsgi.Resource(ActionController(options), deserializer, serializer)
