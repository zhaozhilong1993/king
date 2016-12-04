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

from keystoneauth1 import session
from keystoneauth1.identity import v3
from king.common import config


@six.add_metaclass(abc.ABCMeta)
class ClientPlugin(object):

    _get_client_option = staticmethod(config.get_client_option)

    def __init__(self, context, client=None):
        self._context = weakref.ref(context)
        self._keystone_session_obj = None
        self.king = None
        self.client = client
        auth = v3.Password(auth_url="http://10.0.200.41:5000/v3",
                           username="admin",
                           password="ccbce9a165cb47c40242bc4c",
                           project_name="openstack",
                           user_domain_id="default",
                           project_domain_id="default")
        self.sess = session.Session(auth=auth)
