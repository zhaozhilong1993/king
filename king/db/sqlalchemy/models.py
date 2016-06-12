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
import uuid
import six
import sqlalchemy
from sqlalchemy.orm import session as orm_session
from sqlalchemy.ext import declarative



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


class Volume(BASE, KingBase, SoftDelete):

    __tablename__ = 'volume'

    id = sqlalchemy.Column('id',
                           sqlalchemy.String(36),
                           primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    user_id = sqlalchemy.Column('user_id',
                                sqlalchemy.String(36),
                                nullable=False)
    volume_num = sqlalchemy.Column('volume_num',
                                  sqlalchemy.Integer(),
                                  nullable=True)
    volume_size = sqlalchemy.Column('volume_size',
                                 sqlalchemy.String(255),
                                 nullable=True)
