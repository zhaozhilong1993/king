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

import six
from webob import exc


def policy_enforce(handler):
    """Decorator that enforces policies.

    Checks the path matches the request context and enforce policy defined in
    policy.json.

    This is a handler method decorator.
    """
    @six.wraps(handler)
    def handle_method(controller, req, **kwargs):
        allowed = req.context.policy.enforce(context=req.context,
                                             action=handler.__name__,
                                             scope=controller.REQUEST_SCOPE)
        if not allowed:
            raise exc.HTTPForbidden()
        return handler(controller, req, **kwargs)

    return handle_method


PARAM_TYPES = (
    PARAM_TYPE_SINGLE, PARAM_TYPE_MULTI, PARAM_TYPE_MIXED
) = (
    'single', 'multi', 'mixed'
)


def get_allowed_params(params, whitelist):
    """Extract from ``params`` all entries listed in ``whitelist``.

    The returning dict will contain an entry for a key if, and only if,
    there's an entry in ``whitelist`` for that key and at least one entry in
    ``params``. If ``params`` contains multiple entries for the same key, it
    will yield an array of values: ``{key: [v1, v2,...]}``

    :param params: a NestedMultiDict from webob.Request.params
    :param whitelist: an array of strings to whitelist

    :returns: a dict with {key: value} pairs
    """
    allowed_params = {}

    for key, get_type in six.iteritems(whitelist):
        assert get_type in PARAM_TYPES

        value = None
        if get_type == PARAM_TYPE_SINGLE:
            value = params.get(key)
        elif get_type == PARAM_TYPE_MULTI:
            value = params.getall(key)
        elif get_type == PARAM_TYPE_MIXED:
            value = params.getall(key)
            if isinstance(value, list) and len(value) == 1:
                value = value.pop()

        if value:
            allowed_params[key] = value

    return allowed_params
