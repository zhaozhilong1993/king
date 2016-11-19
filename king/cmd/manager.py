#
# All Rights Reserved.
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

"""CLI interface for king management."""

import sys

from oslo_config import cfg
from oslo_log import log

from king.common import context
from king.common.i18n import _
from king.db import api as db_api
from king.db import utils
from king import version


CONF = cfg.CONF


def do_db_version():
    """Print database's current migration level."""
    print(db_api.db_version(db_api.get_engine()))


def do_db_sync():
    """Place a database under migration control and upgrade.

    Creating first if necessary.
    """
    db_api.db_sync(db_api.get_engine(), CONF.command.version)


def do_resource_data_list():
    ctxt = context.get_admin_context()
    data = db_api.resource_data_get_all(ctxt, CONF.command.resource_id)

    print_format = "%-16s %-64s"

    for k in data.keys():
        print(print_format % (k, data[k]))


def purge_deleted():
    """Remove database records that have been previously soft deleted."""
    utils.purge_deleted(CONF.command.age, CONF.command.granularity)


def do_crypt_parameters_and_properties():
    """Encrypt/decrypt hidden parameters and resource properties data."""
    ctxt = context.get_admin_context()
    prev_encryption_key = CONF.command.previous_encryption_key
    if CONF.command.crypt_operation == "encrypt":
        utils.encrypt_parameters_and_properties(ctxt, prev_encryption_key)
    elif CONF.command.crypt_operation == "decrypt":
        utils.decrypt_parameters_and_properties(ctxt, prev_encryption_key)


def add_command_parsers(subparsers):
    # db_version parser
    parser = subparsers.add_parser('db_version')
    parser.set_defaults(func=do_db_version)

    # db_sync parser
    parser = subparsers.add_parser('db_sync')
    parser.set_defaults(func=do_db_sync)
    # positional parameter, can be skipped. default=None
    parser.add_argument('version', nargs='?')

    # purge_deleted parser
    parser = subparsers.add_parser('purge_deleted')
    parser.set_defaults(func=purge_deleted)
    # positional parameter, can be skipped. default='90'
    parser.add_argument('age', nargs='?', default='90',
                        help=_('How long to preserve deleted data.'))
    # optional parameter, can be skipped. default='days'
    parser.add_argument(
        '-g', '--granularity', default='days',
        choices=['days', 'hours', 'minutes', 'seconds'],
        help=_('Granularity to use for age argument, defaults to days.'))

    # update_params parser
    parser = subparsers.add_parser('update_params')
    parser.set_defaults(func=do_crypt_parameters_and_properties)
    # positional parameter, can't be skipped
    parser.add_argument('crypt_operation',
                        choices=['encrypt', 'decrypt'],
                        help=_('Valid values are encrypt or decrypt. The '
                               'king-engine processes must be stopped to use '
                               'this.'))
    # positional parameter, can be skipped. default=None
    parser.add_argument('previous_encryption_key',
                        nargs='?',
                        default=None,
                        help=_('Provide old encryption key. New encryption'
                               ' key would be used from config file.'))

    parser = subparsers.add_parser('resource_data_list')
    parser.set_defaults(func=do_resource_data_list)
    parser.add_argument('resource_id',
                        help=_('Stack resource id'))


command_opt = cfg.SubCommandOpt('command',
                                title='Commands',
                                help='Show available commands.',
                                handler=add_command_parsers)


def main():
    log.register_options(CONF)
    log.setup(CONF, "king-manage")
    CONF.register_cli_opt(command_opt)
    try:
        default_config_files = cfg.find_config_files('king', 'king-engine')
        CONF(sys.argv[1:], project='king', prog='king-manage',
             version=version.version_info.version_string(),
             default_config_files=default_config_files)
    except RuntimeError as e:
        sys.exit("ERROR: %s" % e)

    try:
        CONF.command.func()
    except Exception as e:
        sys.exit("ERROR: %s" % e)
