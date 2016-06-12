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

import abc
import six
import weakref

from oslo_config import cfg

from keystoneauth1 import session
from king.common import config


@six.add_metaclass(abc.ABCMeta)
class ClientPlugin(object):

    _get_client_option = staticmethod(config.get_client_option)

    def __init__(self, context):
        self._context = weakref.ref(context)
        self._keystone_session_obj = None


    @property
    def context(self):
        ctxt = self._context()
        assert ctxt is not None, "Need a reference to the context"
        return ctxt


    @property
    def auth_token(self):
        # NOTE(jamielennox): use the session defined by the keystoneclient
        return self.context.auth_plugin.get_token(self._keystone_session)

    @property
    def _keystone_session(self):
        if not self._keystone_session_obj:
            self._keystone_session_obj = session.Session(
                **config.get_ssl_options('keystone'))
        return self._keystone_session_obj

    def url_for(self, **kwargs):
        def get_endpoint():
            auth_plugin = self.context.auth_plugin
            return auth_plugin.get_endpoint(self._keystone_session, **kwargs)

        # NOTE(jamielennox): use the session defined by the keystoneclient
        # options as traditionally the token was always retrieved from
        # keystoneclient.
        try:
            kwargs.setdefault('interface', kwargs.pop('endpoint_type'))
        except KeyError:
            pass

        reg = self.context.region_name or cfg.CONF.region_name_for_services
        kwargs.setdefault('region_name', reg)
        url = None
        try:
            url = get_endpoint()
        except exceptions.EmptyCatalog:
            auth_plugin = self.context.auth_plugin
            endpoint = auth_plugin.get_endpoint(
                None, interface=plugin.AUTH_INTERFACE)
            token = auth_plugin.get_token(None)
            token_obj = generic.Token(endpoint, token)
            auth_ref = token_obj.get_access(self._keystone_session)
            if auth_ref.has_service_catalog():
                self.context.reload_auth_plugin()
                url = get_endpoint()

        # NOTE(jamielennox): raising exception maintains compatibility with
        # older keystoneclient service catalog searching.
        if url is None:
            raise exceptions.EndpointNotFound()

        return url

