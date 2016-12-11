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

"""Client side of the king server RPC API."""
from king.common import messaging
from king.rpc import api as rpc_api


class ServerClient(object):
    """Client side of the king server rpc API.

    API version history::

        1.0 - Initial version.
    """

    BASE_RPC_API_VERSION = '1.0'

    def __init__(self):
        self._client = messaging.get_rpc_client(
            topic=rpc_api.SERVER_TOPIC,
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

    def cron_create(self, ctxt, order_id):
        """Add cron task for order
        :param ctxt: RPC context.
        """
        return self.call(ctxt,
                         self.make_msg('cron_create',
                                       order_id=order_id),
                         version='1.0')
