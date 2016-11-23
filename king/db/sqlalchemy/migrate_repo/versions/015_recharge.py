
"""empty message

Revision ID: 015
Revises:
Create Date: 2016-03-21 11:01:39.317932

"""
import sqlalchemy

# revision identifiers, used by Alembic.
revision = '015'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    recharge_record = sqlalchemy.Table(
        'recharge_record', meta,
        sqlalchemy.Column('id', sqlalchemy.String(36), primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('account_id', sqlalchemy.String(36),
                          nullable=False),
        sqlalchemy.Column('recharge_method', sqlalchemy.String(255)),
        sqlalchemy.Column('recharge_commend', sqlalchemy.String(255)),
        sqlalchemy.Column('recharge', sqlalchemy.Float),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = (
        recharge_record,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise
