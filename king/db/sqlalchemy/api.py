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

"""Implementation of SQLAlchemy backend."""

from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from oslo_utils import timeutils

from king.common import exception
from king.db.sqlalchemy import migration
from king.db.sqlalchemy import models

import osprofiler.sqlalchemy
import sqlalchemy
from sqlalchemy.orm import session as orm_session
import sys

CONF = cfg.CONF
CONF.import_opt('hidden_stack_tags', 'king.common.config')
CONF.import_group('profiler', 'king.common.config')

_facade = None


def get_facade():
    global _facade

    if not _facade:
        _facade = db_session.EngineFacade.from_config(CONF)
        if CONF.profiler.enabled:
            if CONF.profiler.trace_sqlalchemy:
                osprofiler.sqlalchemy.add_tracing(sqlalchemy,
                                                  _facade.get_engine(),
                                                  "db")

    return _facade


def get_engine():
    return get_facade().get_engine()


def get_session():
    return get_facade().get_session()


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def model_query(context, *args):
    session = _session(context)
    query = session.query(*args)
    return query


def _session(context):
    return (context and context.session) or get_session()


def db_sync(engine, version=None):
    """Migrate the database to `version` or the most recent version."""
    if version is not None and int(version) < db_version(engine):
        raise exception.Error(_("Cannot migrate to lower schema version."))
    return migration.db_sync(engine, version=version)


def db_version(engine):
    """Display the current database version."""
    return migration.db_version(engine)


def service_create(context, values):
    session = get_session()
    service = models.Service()
    service.update(values)
    service.save(session)
    return service


def service_update(context, service_id, values):
    values.update({'updated_at': timeutils.utcnow()})
    service = service_get(context, service_id)
    service.update(values)
    service.save(_session(context))
    return service


def service_get(context, service_id):
    query = model_query(context, models.Service)
    res = query.get(service_id)
    if res is None:
        raise exception.EntityNotFound(entity='Service', name=service_id)
    return res


def service_delete(context, service_id, soft_delete):
    service = service_get(context, service_id)
    session = orm_session.Session.object_session(service)
    with session.begin():
        if soft_delete:
            service.soft_delete(session=session)
        else:
            session.delete(service)


def service_get_all_by_args(context, host, process, hostname):
    query = model_query(context, models.Service)
    res = query.filter_by(host=host,
                          hostname=hostname,
                          process=process).all()
    return res


def valume_quota_get_all(context):
    query = model_query(context, models.Valume)
    res = query.filter_by().all()
    return res
