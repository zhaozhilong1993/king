
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


    service = sqlalchemy.Table(
        'service', meta,
        sqlalchemy.Column('id', sqlalchemy.String(36), primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('engine_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('host', sqlalchemy.String(255)),
        sqlalchemy.Column('hostname', sqlalchemy.String(255)),
        sqlalchemy.Column('process', sqlalchemy.String(255)),
        sqlalchemy.Column('topic', sqlalchemy.String(255)),
        sqlalchemy.Column('report_interval', sqlalchemy.String(255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    order = sqlalchemy.Table(
        'order', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('resource_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('account_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('price_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('order_status', sqlalchemy.String(255)),
        sqlalchemy.Column('order_type', sqlalchemy.String(255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    account = sqlalchemy.Table(
        'account', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('user_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('account_money', sqlalchemy.Float, nullable=False),
        sqlalchemy.Column('account_level', sqlalchemy.Integer),
        sqlalchemy.Column('account_password', sqlalchemy.String(255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    price = sqlalchemy.Table(
        'price', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('resource_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('order_type', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('price_num', sqlalchemy.Float),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    pay_record = sqlalchemy.Table(
        'pay_record', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('order_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('account_id', sqlalchemy.String(36), nullable=False),
        sqlalchemy.Column('pay_action', sqlalchemy.String(255)),
        sqlalchemy.Column('pay', sqlalchemy.Float),
        sqlalchemy.Column('recharge', sqlalchemy.Float),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    order_acction_record = sqlalchemy.Table(
        'order_acction_record', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('order_status_now', sqlalchemy.String(255)),
        sqlalchemy.Column('order_status_change_to', sqlalchemy.String(255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    crontab = sqlalchemy.Table(
        'crontab', meta,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('order_id', sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column('cron_at', sqlalchemy.DateTime, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    tables = (
        order,
        account,
        price,
        order_acction_record,
        pay_record,
        crontab
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise
