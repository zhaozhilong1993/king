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
from king.api.openstack.v1 import users


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

        # Stacks
        users_resource = users.create_resource(conf)
        connect(controller=users_resource,
                # path_prefix='/{tenant_id}',
                path_prefix='',
                routes=[
                    # Template handling
                    {
                        'name': 'user_list',
                        'url': '/users',
                        'action': 'list',
                        'method': 'GET'
                    },
                    {
                        'name': 'user_create',
                        'url': '/users',
                        'action': 'create',
                        'method': 'POST'
                    },
                ])

        # now that all the routes are defined, add a handler for
        super(API, self).__init__(mapper)