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

"""SQLAlchemy models for heat data."""

from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy.ext import declarative
from sqlalchemy.orm import session as orm_session
import six
import sqlalchemy
import uuid


BASE = declarative.declarative_base()


def get_session():
    from heat.db.sqlalchemy import api as db_api
    return db_api.get_session()


class SoftDelete(object):
    deleted_at = sqlalchemy.Column(sqlalchemy.DateTime)

    def soft_delete(self, session=None):
        """Mark this object as deleted."""
        self.update_and_save({'deleted_at': timeutils.utcnow()},
                             session=session)


class KingBase(models.ModelBase, models.TimestampMixin):
    """Base class for Heat Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}

    def expire(self, session=None, attrs=None):
        """Expire this object ()."""
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.expire(self, attrs)

    def refresh(self, session=None, attrs=None):
        """Refresh this object."""
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.refresh(self, attrs)

    def delete(self, session=None):
        """Delete this object."""
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.begin(subtransactions=True)
        session.delete(self)
        session.commit()

    def update_and_save(self, values, session=None):
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.begin(subtransactions=True)
        for k, v in six.iteritems(values):
            setattr(self, k, v)
        session.commit()


class Service(BASE, KingBase, SoftDelete):

    __tablename__ = 'service'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    engine_id = sqlalchemy.Column('engine_id',
                                  sqlalchemy.String(36),
                                  nullable=False)
    host = sqlalchemy.Column('host',
                             sqlalchemy.String(255),
                             nullable=False)
    hostname = sqlalchemy.Column('hostname',
                                 sqlalchemy.String(255),
                                 nullable=False)
    process = sqlalchemy.Column('process',
                                sqlalchemy.String(255),
                                nullable=False)
    topic = sqlalchemy.Column('topic',
                              sqlalchemy.String(255),
                              nullable=False)
    report_interval = sqlalchemy.Column('report_interval',
                                        sqlalchemy.Integer,
                                        nullable=False)


class Order(BASE, KingBase, SoftDelete):
    __tablename__ = 'order'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    resource_id = sqlalchemy.Column('resource_id',
                                    sqlalchemy.String(36),
                                    nullable=False)
    project_id = sqlalchemy.Column('project_id',
                                   sqlalchemy.String(36),
                                   nullable=False)
    price_id = sqlalchemy.Column('price_id',
                                 sqlalchemy.String(36),
                                 nullable=False)
    order_status = sqlalchemy.Column('order_status',
                                     sqlalchemy.String(255),
                                     nullable=True)
    order_type = sqlalchemy.Column('order_type',
                                   sqlalchemy.String(255),
                                   nullable=True)
    created_at = sqlalchemy.Column('created_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    updated_at = sqlalchemy.Column('updated_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    deleted_at = sqlalchemy.Column('deleted_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)


class Account(BASE, KingBase, SoftDelete):
    __tablename__ = 'account'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    user_id = sqlalchemy.Column('user_id',
                                sqlalchemy.String(36),
                                nullable=False)
    account_money = sqlalchemy.Column('account_money',
                                      sqlalchemy.Float,
                                      default=10.0,
                                      nullable=True)
    account_level = sqlalchemy.Column('account_level',
                                      sqlalchemy.Integer,
                                      default=3,
                                      nullable=True)
    account_password = sqlalchemy.Column('account_password',
                                         sqlalchemy.String(255),
                                         nullable=True)
    created_at = sqlalchemy.Column('created_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    updated_at = sqlalchemy.Column('updated_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    deleted_at = sqlalchemy.Column('deleted_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)


class Price(BASE, KingBase, SoftDelete):
    __tablename__ = 'price'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    resource_type = sqlalchemy.Column('resource_type',
                                      sqlalchemy.String(36),
                                      nullable=False)
    resource_id = sqlalchemy.Column('resource_id',
                                    sqlalchemy.String(36),
                                    nullable=False)
    order_type = sqlalchemy.Column('order_type',
                                   sqlalchemy.String(36),
                                   nullable=True)
    price_num = sqlalchemy.Column('price_num',
                                  sqlalchemy.Float,
                                  nullable=True)
    created_at = sqlalchemy.Column('created_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    updated_at = sqlalchemy.Column('updated_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    deleted_at = sqlalchemy.Column('deleted_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)


class Action_record(BASE, KingBase, SoftDelete):
    __tablename__ = 'action_record'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    resource_id = sqlalchemy.Column('resource_id',
                                    sqlalchemy.String(36),
                                    nullable=False)
    user_id = sqlalchemy.Column('user_id',
                                sqlalchemy.String(36),
                                nullable=False)
    project_id = sqlalchemy.Column('project_id',
                                   sqlalchemy.String(36),
                                   nullable=False)
    created_at = sqlalchemy.Column('created_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    updated_at = sqlalchemy.Column('updated_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    deleted_at = sqlalchemy.Column('deleted_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    resource_type = sqlalchemy.Column('resource_type',
                                      sqlalchemy.String(255),
                                      nullable=True)
    action = sqlalchemy.Column('action',
                               sqlalchemy.String(255),
                               nullable=True)


class Pay_record(BASE, KingBase, SoftDelete):
    __tablename__ = 'pay_record'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    order_id = sqlalchemy.Column('order_id',
                                 sqlalchemy.String(36),
                                 nullable=False)
    user_id = sqlalchemy.Column('user_id',
                                sqlalchemy.String(36),
                                nullable=False)
    project_id = sqlalchemy.Column('project_id',
                                   sqlalchemy.String(36),
                                   nullable=False)
    pay_action = sqlalchemy.Column('pay_action',
                                   sqlalchemy.String(255),
                                   nullable=True)
    pay = sqlalchemy.Column('pay',
                            sqlalchemy.Float,
                            nullable=True)
    created_at = sqlalchemy.Column('created_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    updated_at = sqlalchemy.Column('updated_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    deleted_at = sqlalchemy.Column('deleted_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)


class Recharge_record(BASE, KingBase, SoftDelete):
    __tablename__ = 'recharge_record'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    account_id = sqlalchemy.Column('account_id',
                                   sqlalchemy.String(36),
                                   nullable=False)
    recharge_method = sqlalchemy.Column('recharge_method',
                                        sqlalchemy.String(255),
                                        nullable=False)
    recharge_commend = sqlalchemy.Column('recharge_commend',
                                         sqlalchemy.String(255),
                                         nullable=True)
    recharge = sqlalchemy.Column('recharge',
                                 sqlalchemy.Float,
                                 nullable=True)
    created_at = sqlalchemy.Column('created_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    updated_at = sqlalchemy.Column('updated_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)
    deleted_at = sqlalchemy.Column('deleted_at',
                                   sqlalchemy.DateTime,
                                   nullable=True)


class Crontab(BASE, KingBase, SoftDelete):
    __tablename__ = 'Crontab'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    order_id = sqlalchemy.Column('order_id',
                                 sqlalchemy.String(36),
                                 nullable=False)
    cron_at = sqlalchemy.Column('cron_at',
                                sqlalchemy.DateTime,
                                nullable=True)
