#
# Copyright 2012, Red Hat, Inc.
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

"""Client side of the heat engine RPC API."""

from oslo_utils import reflection

from king.common import messaging
from king.rpc import api as rpc_api


class EngineClient(object):
    """Client side of the heat engine rpc API.

    API version history::

        1.0 - Initial version.
    """

    BASE_RPC_API_VERSION = '1.0'

    def __init__(self):
        self._client = messaging.get_rpc_client(
            topic=rpc_api.ENGINE_TOPIC,
            version=self.BASE_RPC_API_VERSION)

    @staticmethod
    def make_msg(method, **kwargs):
        return method, kwargs

    def call(self, ctxt, msg, version=None, timeout=None):
        method, kwargs = msg

        if version is not None:
            client = self._client.prepare(version=version)
        else:
            client = self._client

        if timeout is not None:
            client = client.prepare(timeout=timeout)

        return client.call(ctxt, method, **kwargs)

    def cast(self, ctxt, msg, version=None):
        method, kwargs = msg
        if version is not None:
            client = self._client.prepare(version=version)
        else:
            client = self._client
        return client.cast(ctxt, method, **kwargs)


    def list_quota(self, ctxt):
        """Returns the full quota.

        :param ctxt: RPC context.
        :param user: the quota of this user
        """
        return self.call(ctxt, self.make_msg('list_quota'), version='1.0')


    def list_default_quota(self, ctxt):
        """Returns the full quota.

        :param ctxt: RPC context.
        :param user: the quota of this user
        """
        return self.call(ctxt, self.make_msg('list_default_quota'), version='1.0')

