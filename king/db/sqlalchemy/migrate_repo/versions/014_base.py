
"""empty message

Revision ID: 014
Revises: 
Create Date: 2016-03-21 11:01:39.317932

"""

# revision identifiers, used by Alembic.
revision = '014'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    user = sqlalchemy.Table(
        'user', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('user_id', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('user_name', sqlalchemy.String(64), nullable=False, unique=True),
        sqlalchemy.Column('user_email', sqlalchemy.String(255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = (
        user,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise