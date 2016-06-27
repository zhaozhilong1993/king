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

import routes
import six

from king.common import wsgi
from king.api.openstack.v1 import quota
from king.api.openstack.v1 import volume
from king.api.openstack.v1 import services


class API(wsgi.Router):

    """WSGI router for King v1 REST API requests."""

    def __init__(self, conf, **local_conf):
        self.conf = conf
        mapper = routes.Mapper()
        default_resource = wsgi.Resource(wsgi.DefaultMethodController(),
                                         wsgi.JSONRequestDeserializer())

        def connect(controller, path_prefix, routes):
            """Connects list of routes to given controller with path_prefix.

            This function connects the list of routes to the given
            controller, prepending the given path_prefix. Then for each URL it
            finds which request methods aren't handled and configures those
            to return a 405 error. Finally, it adds a handler for the
            OPTIONS method to all URLs that returns the list of allowed
            methods with 204 status code.
            """
            # register the routes with the mapper, while keeping track of which
            # methods are defined for each URL
            urls = {}

            for r in routes:
                url = path_prefix + r['url']
                methods = r['method']
                if isinstance(methods, six.string_types):
                    methods = [methods]
                methods_str = ','.join(methods)

                # function run like :
                # mapper.connect(
                #  'stack_list',
                #   '/stack',
                #   controller=controller,
                #   action='GET',
                #   conditions={'method':'GET'}
                # )
                mapper.connect(r['name'], url, controller=controller,
                               action=r['action'],
                               conditions={'method': methods_str})
                if url not in urls:
                    urls[url] = methods
                else:
                    urls[url] += methods

            # now register the missing methods to return 405s, and register
            # a handler for OPTIONS that returns the list of allowed methods
            for url, methods in urls.items():
                all_methods = ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                missing_methods = [m for m in all_methods if m not in methods]
                allowed_methods_str = ','.join(methods)
                mapper.connect(url,
                               controller=default_resource,
                               action='reject',
                               allowed_methods=allowed_methods_str,
                               conditions={'method': missing_methods})
                if 'OPTIONS' not in methods:
                    mapper.connect(url,
                                   controller=default_resource,
                                   action='options',
                                   allowed_methods=allowed_methods_str,
                                   conditions={'method': 'OPTIONS'})
        # service
        services_resource = services.create_resource(conf)
        connect(controller=services_resource,
                path_prefix='',
                routes=[
                    {
                        'name': 'services_list',
                        'url': '/services',
                        'action': 'list',
                        'method': 'GET'
                    }
                ]
        )

        # quota
        quotas_resource = quota.create_resource(conf)
        connect(controller=quotas_resource,
                # path_prefix='/{tenant_id}',
                path_prefix='',
                routes=[
                    {
                        'name': 'quota_list',
                        'url': '/quota',
                        'action': 'list',
                        'method': 'GET'
                    },
                    {
                        'name': 'quota_list_default',
                        'url': '/quota/default',
                        'action': 'list_default',
                        'method': 'GET'
                    },
                    {
                        'name': 'update_quota',
                        'url': '/quota',
                        'action': 'update_quota',
                        'method': 'POST'
                    },
                    {
                        'name': 'quota_show',
                        'url': '/quota/detail',
                        'action': 'show',
                        'method': 'POST'
                    }
                ])

        volume_resource = volume.create_resource(conf)
        connect(controller=volume_resource,
                # path_prefix='/{tenant_id}',
                path_prefix='',
                routes=[
                    {
                        'name': 'create_volume',
                        'url': '/volume',
                        'action': 'create',
                        'method': 'POST'
                    },
                ])
        # now that all the routes are defined, add a handler for
        super(API, self).__init__(mapper)
