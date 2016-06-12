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

from king.server.clients.os import cinder
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

class Volume(object):
    def __init__(self, context):
        self.client = cinder.BaseCinder(context)

    def _volume_format(self, volume):
        res = {}
        res['id'] = volume.id
        res['name'] = volume.name
        res['links'] = volume.links
        return res

    def list(self):
        pass

    def create(self, volume):
        volume = self.client.create_volume(volume)
        res = self._volume_format(volume)
        return res
