
"""empty message

Revision ID: 015
Revises: 
Create Date: 2016-03-21 11:01:39.317932

"""

# revision identifiers, used by Alembic.
revision = '015'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy
import uuid

def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    service = sqlalchemy.Table(
        'service', meta,
        sqlalchemy.Column('id', sqlalchemy.String(36), primary_key=True,
                          default=lambda: str(uuid.uuid4())),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('engine_id', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('host', sqlalchemy.String(64), nullable=False),
        sqlalchemy.Column('hostname', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('process', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('topic', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('report_interval', sqlalchemy.Integer, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = (
        service,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise