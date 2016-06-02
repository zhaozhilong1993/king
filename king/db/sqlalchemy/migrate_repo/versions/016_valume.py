
"""empty message

Revision ID: 016
Revises: 
Create Date: 2016-06-01 11:01:39.317932

"""

# revision identifiers, used by Alembic.
revision = '016'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy
import uuid

def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    valume = sqlalchemy.Table(
        'valume', meta,
        sqlalchemy.Column('id', sqlalchemy.String(36), primary_key=True,
                          default=lambda: str(uuid.uuid4())),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('user_id', sqlalchemy.String(255), nullable=False,index=True),
        sqlalchemy.Column('valume_num', sqlalchemy.Integer, nullable=True),
        sqlalchemy.Column('valume_size', sqlalchemy.String(255), nullable=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = (
        valume,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise
