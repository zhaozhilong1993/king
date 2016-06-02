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

from cinderclient import client as cc
from cinderclient import exceptions
from keystoneclient import exceptions as ks_exceptions
from oslo_log import log as logging

from king.common import exception
from king.server.clients import client_plugin


LOG = logging.getLogger(__name__)

CLIENT_NAME = 'cinder'

class BaseCinder(client_plugin.ClientPlugin):
    def create_valume(self):
        pass
