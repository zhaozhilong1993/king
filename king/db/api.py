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


def service_delete(context, service_id, soft_delete):
    return IMPL.service_delete(context, service_id, soft_delete)


def service_get_all_by_args(context, host, process, hostname):
    return IMPL.service_get_all_by_args(context, host, process, hostname)


def valume_quota_get_all(context):
    return IMPL.valume_quota_get_all(context)

def valume_quota_update(context, user_id, values):
    return IMPL.valume_quota_update(context, user_id, values)