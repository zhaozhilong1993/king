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

"""Interface for database access."""

from oslo_config import cfg
from oslo_db import api

CONF = cfg.CONF


_BACKEND_MAPPING = {'sqlalchemy': 'king.db.sqlalchemy.api'}

IMPL = api.DBAPI.from_config(CONF, backend_mapping=_BACKEND_MAPPING)


def get_engine():
    return IMPL.get_engine()


def get_session():
    return IMPL.get_session()


def db_sync(engine, version=None):
    """Migrate the database to `version` or the most recent version."""
    return IMPL.db_sync(engine, version=version)


def db_version(engine):
    """Display the current database version."""
    return IMPL.db_version(engine)


def service_create(context, values):
    return IMPL.service_create(context, values)


def service_update(context, service_id, values):
    return IMPL.service_update(context, service_id, values)


def service_get(context, service_id):
    return IMPL.service_get(context, service_id)


def service_get_all(context):
    return IMPL.service_get_all(context)


def service_delete(context, service_id, soft_delete):
    return IMPL.service_delete(context, service_id, soft_delete)


def service_get_all_by_args(context, host, process, hostname):
    return IMPL.service_get_all_by_args(context, host, process, hostname)


def order_get(context, resource_id=None, order_id=None):
    return IMPL.order_get(context, resource_id=resource_id, order_id=order_id)


def order_get_all(context):
    return IMPL.order_get_all(context)


def order_create(context, value):
    return IMPL.order_create(context, value)


def order_update_status(context, order_id, status):
    return IMPL.order_update_status(context, order_id, status)


def price_create(context, value):
    return IMPL.price_create(context, value)


def price_get(context, price_id):
    return IMPL.price_get(context, price_id)


def account_get(context, user_id):
    return IMPL.account_get(context, user_id)


def account_create(context, value):
    return IMPL.account_create(context, value)


def account_pay_money(context, user_id, project_id, order_id, pay_money):
    return IMPL.account_pay_money(context,
                                  user_id,
                                  project_id,
                                  order_id,
                                  pay_money)


def account_recharge_money(context, value):
    return IMPL.account_recharge_money(context, value)


def action_record(context, value):
    return IMPL.action_record(context, value)
