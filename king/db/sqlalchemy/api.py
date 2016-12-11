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
from oslo_log import log as logging
from oslo_db.sqlalchemy import session as db_session
from oslo_utils import timeutils
from king.common.i18n import _
from king.common.i18n import _LE

from king.common import exception
from king.db.sqlalchemy import migration
from king.db.sqlalchemy import models

import osprofiler.sqlalchemy
import sqlalchemy
from sqlalchemy.orm import session as orm_session
import sys

LOG = logging.getLogger(__name__)

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


def service_get_all(context):
    return (model_query(context, models.Service).
            filter_by(deleted_at=None).all())


def service_get_all_by_args(context, host, process, hostname):
    query = model_query(context, models.Service)
    res = query.filter_by(host=host,
                          hostname=hostname,
                          process=process).all()
    return res


def order_get_all(context):
    return (model_query(context, models.Order).
            filter_by(deleted_at=None).all())


def order_get(context, resource_id=None, order_id=None):
    query = model_query(context, models.Order)
    if order_id:
        res = query.get(order_id)
        if res is None:
            LOG.error(_LE('resouce_id : %s do not have a order' % resource_id))
            raise exception.EntityNotFound(entity='Order', name=resource_id)
        return res
    elif resource_id:
        res = query.get(resource_id)
        if res is None:
            LOG.error(_LE('resouce_id : %s do not have a order' % resource_id))
            raise exception.EntityNotFound(entity='Order', name=resource_id)
        return res
    else:
        LOG.error("resource_id or order_id is necessary.")
        raise exception.EntityNotFound(entity='Order',
                                       name="resource_id or order_id")


def order_create(context, value):
    value['created_at'] = timeutils.utcnow()
    value['order_status'] = "RUNNING"
    session = get_session()
    order = models.Order()
    order.update(value)
    order.save(session)
    return order


def order_update_status(context, order_id, status):
    order = order_get(context, order_id)
    value = {'order_status': status,
             'updated_at': timeutils.utcnow()}
    order.update(value)
    order.save(_session(context))
    return order


def price_create(context, value):
    value['created_at'] = timeutils.utcnow()
    session = get_session()
    price = models.Price()
    price.update(value)
    price.save(session)
    return price


def price_get(context, price_id):
    query = model_query(context, models.Price)
    res = query.get(price_id)
    if res is None:
        raise exception.EntityNotFound(entity='Price', name=price_id)
    return res


def account_get(context, user_id):
    query = model_query(context, models.Account)
    res = query.filter_by(user_id=user_id).first()
    if res is None:
        raise exception.EntityNotFound(entity='Account', name=user_id)
    return res


def account_create(context, value):
    value['created_at'] = timeutils.utcnow()
    session = get_session()
    account = models.Account()
    account.update(value)
    account.save(session)
    return account


def account_pay_money(context, user_id, project_id,
                      order_id, pay_money, pay_action=None):
    account = account_get(context, user_id)
    value = {'updated_at': timeutils.utcnow(),
             'account_money': account.account_money - pay_money}
    account.update(value)
    account.save(_session(context))
    pay_record(context, {'order_id': order_id,
                         'user_id': user_id,
                         'project_id': project_id,
                         'pay_action': pay_action,
                         'pay': pay_money,
                         'created_at': value['updated_at']})
    return account


def account_recharge_money(context, data):
    account = account_get(context, data['account_id'])
    value = {'updated_at': timeutils.utcnow(),
             'account_money': account.account_money + data['recharge']}
    account.update(value)
    account.save(_session(context))
    recharge_record(context, data)
    return account


def recharge_record(context, data):
    session = get_session()
    recharge_record = models.Recharge_record()
    recharge_record.update(data)
    recharge_record.save(session)


def pay_record(context, value):
    session = get_session()
    pay_record = models.Pay_record()
    pay_record.update(value)
    pay_record.save(session)
    return pay_record


def action_record(context, data):
    data['created_at'] = timeutils.utcnow()
    session = get_session()
    action_record = models.Action_record()
    action_record.update(data)
    action_record.save(session)
    return action_record


def action_record_get(context, resource_id, start=None, end=None):
    query = model_query(context, models.Action_record)
    res = query.filter_by(resource_id=resource_id)
    return res
