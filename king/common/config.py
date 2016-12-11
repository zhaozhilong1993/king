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

"""Routines for configuring King."""
import os

from eventlet.green import socket
from oslo_config import cfg
from oslo_log import log as logging

from king.common.i18n import _
from king.common import wsgi


LOG = logging.getLogger(__name__)
paste_deploy_group = cfg.OptGroup('paste_deploy')
paste_deploy_opts = [
    cfg.StrOpt('flavor',
               help=_("The flavor to use.")),
    cfg.StrOpt('api_paste_config', default="api-paste.ini",
               help=_("The API paste config file to use."))]


service_opts = [
    cfg.IntOpt('periodic_interval',
               default=60,
               help=_('Seconds between running periodic tasks.')),
    cfg.IntOpt('deduction_interval',
               default=1,
               help=_('mins between running deduction tasks.')),
    cfg.StrOpt('region_name_for_services',
               default="RegionOne",
               help=_('Default region name used to get services endpoints.')),
    cfg.IntOpt('num_engine_workers',
               default=1,
               help=_('Number of king-engine processes to fork and run.'))]

account_opts = [
    cfg.IntOpt('periodic_interval',
               default=60,
               help=_('Seconds between running periodic tasks.')),
    cfg.IntOpt('num_account_workers',
               default=1,
               help=_('Number of king-engine processes to fork and run.'))]


engine_opts = [
    cfg.ListOpt('plugin_dirs',
                default=['/usr/lib64/king', '/usr/lib/king',
                         '/usr/local/lib/king', '/usr/local/lib64/king'],
                help=_('List of directories to search for plug-ins.')),
    cfg.StrOpt('environment_dir',
               default='/etc/king/environment.d',
               help=_('The directory to search for environment files.')),
    cfg.IntOpt('stale_token_duration',
               default=30,
               help=_('Gap, in seconds, to determine whether the given token '
                      'is about to expire.'),),
    cfg.IntOpt('event_purge_batch_size',
               default=10,
               help=_("Controls how many events will be pruned whenever a "
                      "stack's events exceed max_events_per_stack. Set this "
                      "lower to keep more events at the expense of more "
                      "frequent purges.")),
    cfg.IntOpt('error_wait_time',
               default=240,
               help=_('Error wait time in seconds for stack action (ie. create'
                      ' or update).')),
    cfg.IntOpt('engine_life_check_timeout',
               default=2,
               help=_('RPC timeout for the engine liveness check that is used'
                      ' for stack locking.')),
    cfg.BoolOpt('convergence_engine',
                default=False,
                help=_('Enables engine with convergence architecture. All '
                       'stacks with this option will be created using '
                       'convergence engine.')),
    cfg.BoolOpt('observe_on_update',
                default=False,
                help=_('On update, enables king to collect existing resource '
                       'properties from reality and converge to '
                       'updated template.')),
    cfg.StrOpt('default_software_config_transport',
               choices=['POLL_SERVER_CFN',
                        'POLL_SERVER_HEAT',
                        'POLL_TEMP_URL',
                        'ZAQAR_MESSAGE'],
               default='POLL_SERVER_CFN',
               help=_('Template default for how the server should receive the '
                      'metadata required for software configuration. '
                      'POLL_SERVER_CFN will allow calls to the cfn API action '
                      'DescribeStackResource authenticated with the provided '
                      'keypair (requires enabled king-api-cfn). '
                      'POLL_SERVER_HEAT will allow calls to the '
                      'King API resource-show using the provided keystone '
                      'credentials (requires keystone v3 API, and configured '
                      'stack_user_* config options). '
                      'POLL_TEMP_URL will create and populate a '
                      'Swift TempURL with metadata for polling (requires '
                      'object-store endpoint which supports TempURL).'
                      'ZAQAR_MESSAGE will create a dedicated zaqar queue and '
                      'post the metadata for polling.')),
    cfg.StrOpt('default_deployment_signal_transport',
               choices=['CFN_SIGNAL',
                        'TEMP_URL_SIGNAL',
                        'HEAT_SIGNAL',
                        'ZAQAR_SIGNAL'],
               default='CFN_SIGNAL',
               help=_('Template default for how the server should signal to '
                      'king with the deployment output values. CFN_SIGNAL '
                      'will allow an HTTP POST to a CFN keypair signed URL '
                      '(requires enabled king-api-cfn). '
                      'TEMP_URL_SIGNAL will create a Swift TempURL to be '
                      'signaled via HTTP PUT (requires object-store endpoint '
                      'which supports TempURL). '
                      'HEAT_SIGNAL will allow calls to the King API '
                      'resource-signal using the provided keystone '
                      'credentials. ZAQAR_SIGNAL will create a dedicated '
                      'zaqar queue to be signaled using the provided keystone '
                      'credentials.')),
    cfg.ListOpt('hidden_stack_tags',
                default=['data-processing-cluster'],
                help=_('Stacks containing these tag names will be hidden. '
                       'Multiple tags should be given in a comma-delimited '
                       'list (eg. hidden_stack_tags=hide_me,me_too).')),
    cfg.StrOpt('onready',
               help=_('Deprecated.')),
    cfg.BoolOpt('encrypt_parameters_and_properties',
                default=False,
                help=_('Encrypt template parameters that were marked as'
                       ' hidden and also all the resource properties before'
                       ' storing them in database.'))]

rpc_opts = [
    cfg.StrOpt('host',
               default=socket.gethostname(),
               help=_('Name of the engine node. '
                      'This can be an opaque identifier. '
                      'It is not necessarily a hostname, FQDN, '
                      'or IP address.'))]

profiler_group = cfg.OptGroup('profiler')
profiler_opts = [
    cfg.BoolOpt("enabled", default=False,
                help=_('If False fully disable profiling feature.')),
    cfg.BoolOpt("trace_sqlalchemy", default=False,
                help=_("If False do not trace SQL requests.")),
    cfg.StrOpt("hmac_keys", default="SECRET_KEY",
               help=_("Secret key to use to sign tracing messages."))
]

auth_password_group = cfg.OptGroup('auth_password')
auth_password_opts = [
    cfg.StrOpt('auth_url',
               default='http://10.0.200.41:5000/v3',
               help=_('Auth url for keystone')),
    cfg.StrOpt('username',
               default='admin',
               help=_('Keystone admin user name')),
    cfg.StrOpt('password',
               default='ccbce9a165cb47c40242bc4c',
               help=_('Keystone admin user password')),
    cfg.StrOpt('project_name',
               default='openstack',
               help=_('Keystone admin user project name')),
    cfg.StrOpt('user_domain_id',
               default='default',
               help=_('Keystone admin user domain')),
    cfg.StrOpt('project_domain_id',
               default='default',
               help=_('Keystone admin user domain id'))]


# these options define baseline defaults that apply to all clients
clients_opts = [
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help=_(
                   'Type of endpoint in Identity service catalog to use '
                   'for communication with the OpenStack service.')),
    cfg.StrOpt('ca_file',
               help=_('Optional CA cert file to use in SSL connections.')),
    cfg.StrOpt('cert_file',
               help=_('Optional PEM-formatted certificate chain file.')),
    cfg.StrOpt('key_file',
               help=_('Optional PEM-formatted file that contains the '
                      'private key.')),
    cfg.BoolOpt('insecure',
                default=False,
                help=_("If set, then the server's certificate will not "
                       "be verified."))]


king_client_opts = [
    cfg.StrOpt('url',
               default='',
               help=_('Optional king url in format like'
                      ' http://0.0.0.0:9000/v1/%(tenant_id)s.'))]

keystone_client_opts = [
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help=_(
                   'Type of endpoint in Identity service catalog to use '
                   'for communication with the OpenStack service.')),
    cfg.StrOpt('auth_uri',
               default='',
               help=_('Unversioned keystone url in format like'
                      ' http://0.0.0.0:5000.'))]

client_http_log_debug_opts = [
    cfg.BoolOpt('http_log_debug',
                default=False,
                help=_("Allow client's debug log output."))]

revision_group = cfg.OptGroup('revision')
revision_opts = [
    cfg.StrOpt('king_revision',
               default='unknown',
               help=_('King build revision. '
                      'If you would prefer to manage your build revision '
                      'separately, you can move this section to a different '
                      'file and add it as another config option.'))]


def startup_sanity_check():
    '''you can check the config value here'''
    pass


def list_opts():
    yield None, rpc_opts
    yield None, engine_opts
    yield None, service_opts
    yield None, account_opts
    yield paste_deploy_group.name, paste_deploy_opts
    yield auth_password_group.name, auth_password_opts
    yield revision_group.name, revision_opts
    yield profiler_group.name, profiler_opts
    yield 'clients', clients_opts

    for client in ('barbican', 'ceilometer', 'cinder', 'designate', 'glance',
                   'heat', 'keystone', 'magnum', 'manila', 'mistral',
                   'neutron', 'nova', 'sahara', 'senlin', 'swift', 'trove',
                   'zaqar', 'king'):
        client_specific_group = 'clients_' + client
        yield client_specific_group, clients_opts

    yield 'clients_king', king_client_opts
    yield 'clients_keystone', keystone_client_opts
    yield 'clients_nova', client_http_log_debug_opts
    yield 'clients_cinder', client_http_log_debug_opts


cfg.CONF.register_group(paste_deploy_group)
cfg.CONF.register_group(auth_password_group)
cfg.CONF.register_group(revision_group)
cfg.CONF.register_group(profiler_group)

for group, opts in list_opts():
    cfg.CONF.register_opts(opts, group=group)


def _get_deployment_flavor():
    """Retrieves the paste_deploy.flavor config item.

    Item formatted appropriately for appending to the application name.
    """
    flavor = cfg.CONF.paste_deploy.flavor
    return '' if not flavor else ('-' + flavor)


def _get_deployment_config_file():
    """Retrieves the deployment_config_file config item.

    Item formatted as an absolute pathname.
    """
    config_path = cfg.CONF.find_file(
        cfg.CONF.paste_deploy['api_paste_config'])
    if config_path is None:
        return None

    return os.path.abspath(config_path)


def load_paste_app(app_name=None):
    """Builds and returns a WSGI app from a paste config file.

    We assume the last config file specified in the supplied ConfigOpts
    object is the paste config file.

    :param app_name: name of the application to load

    :raises RuntimeError when config file cannot be located or application
            cannot be loaded from config file
    """
    if app_name is None:
        app_name = cfg.CONF.prog

    # append the deployment flavor to the application name,
    # in order to identify the appropriate paste pipeline
    app_name += _get_deployment_flavor()

    conf_file = _get_deployment_config_file()
    if conf_file is None:
        raise RuntimeError(_("Unable to locate config file [%s]") %
                           cfg.CONF.paste_deploy['api_paste_config'])

    try:
        app = wsgi.paste_deploy_app(conf_file, app_name, cfg.CONF)

        # Log the options used when starting if we're in debug mode...
        if cfg.CONF.debug:
            cfg.CONF.log_opt_values(logging.getLogger(app_name),
                                    logging.DEBUG)

        return app
    except (LookupError, ImportError) as e:
        raise RuntimeError(_("Unable to load %(app_name)s from "
                             "configuration file %(conf_file)s."
                             "\nGot: %(e)r") % {'app_name': app_name,
                                                'conf_file': conf_file,
                                                'e': e})


def get_client_option(client, option):
    # look for the option in the [clients_${client}] section
    # unknown options raise cfg.NoSuchOptError
    try:
        group_name = 'clients_' + client
        cfg.CONF.import_opt(option, 'king.common.config',
                            group=group_name)
        v = getattr(getattr(cfg.CONF, group_name), option)
        if v is not None:
            return v
    except cfg.NoSuchGroupError:
        pass  # do not error if the client is unknown
    # look for the option in the generic [clients] section
    cfg.CONF.import_opt(option, 'king.common.config', group='clients')
    return getattr(cfg.CONF.clients, option)


def get_ssl_options(client):
    # Look for the ssl options in the [clients_${client}] section
    cacert = get_client_option(client, 'ca_file')
    insecure = get_client_option(client, 'insecure')
    cert = get_client_option(client, 'cert_file')
    key = get_client_option(client, 'key_file')
    if insecure:
        verify = False
    else:
        verify = cacert or True
    if cert and key:
        cert = (cert, key)
    return {'verify': verify, 'cert': cert}
