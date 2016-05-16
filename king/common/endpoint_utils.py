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
#
#    Copyright 2015 IBM Corp.

from keystoneclient import discover as ks_discover
from oslo_config import cfg
from oslo_utils import importutils

from king.common import config


def get_auth_uri(v3=True):
    # Look for the keystone auth_uri in the configuration. First we
    # check the [clients_keystone] section, and if it is not set we
    # look in [keystone_authtoken]
    if cfg.CONF.clients_keystone.auth_uri:
        discover = ks_discover.Discover(
            auth_url=cfg.CONF.clients_keystone.auth_uri,
            cacert=config.get_client_option('keystone', 'ca_file'),
            insecure=config.get_client_option('keystone', 'insecure'),
            cert=config.get_client_option('keystone', 'cert_file'),
            key=config.get_client_option('keystone', 'key_file'))
        return discover.url_for('3.0')
    else:
        # Import auth_token to have keystone_authtoken settings setup.
        importutils.import_module('keystonemiddleware.auth_token')
        auth_uri = cfg.CONF.keystone_authtoken.auth_uri
        return auth_uri.replace('v2.0', 'v3') if auth_uri and v3 else auth_uri
