
"""empty message

Revision ID: 017
Revises:
Create Date: 2016-06-01 11:01:39.317932

"""

# revision identifiers, used by Alembic.
revision = '017'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.compiler import compiles
import uuid
import time
import datetime


@compiles(CreateTable, "mysql")
def add_partition_scheme(element, compiler, **kw):
    table = element.element
    partition_by = table.kwargs.pop("mysql_partition_by", None)
    partitions = table.kwargs.pop("mysql_partitions", None)
    next_time = int(time.time() + 60*60*24)

    ddl = compiler.visit_create_table(element, **kw)
    ddl = ddl.rstrip()

    if partition_by:
        ddl += "\nPARTITION BY %s (" % partition_by
        table.kwargs['mysql_partition_by'] = partition_by
    if partitions:
        ddl += "\nPARTITION p%s VALUES LESS THAN (%s));" % (partitions,next_time)
        table.kwargs['mysql_partitions'] = partitions

    return ddl


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine
    dateArray = datetime.datetime.utcfromtimestamp(int(time.time()))

    test = sqlalchemy.Table(
        'test', meta,
        sqlalchemy.Column('id', sqlalchemy.String(36),primary_key=True,
                          default=lambda: str(uuid.uuid4())),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('amount', sqlalchemy.DECIMAL(7, 2)),
        sqlalchemy.Column('tr_date', sqlalchemy.Integer, primary_key=True),

        mysql_engine='InnoDB',
        mysql_charset='utf8',
        mysql_partition_by='RANGE(tr_date)',
        mysql_partitions='6'
    )

    tables = (
        test,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise
