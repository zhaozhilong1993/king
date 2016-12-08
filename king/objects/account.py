#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""Account object."""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from king.db import api as db_api
from king.objects import base as king_base


class Account(
        king_base.KingObject,
        base.VersionedObjectDictCompat,
        base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'user_id': fields.StringField(),
        'account_money': fields.StringField(),
        'account_level': fields.StringField(),
        'account_password': fields.StringField(),
        'deleted_at': fields.DateTimeField(),
        'created_at': fields.DateTimeField(),
        'updated_at': fields.DateTimeField()
    }

    @staticmethod
    def _from_db_object(context, account, db_account):
        '''once we finish database action, we need to format the result'''
        for field in account.fields:
            account[field] = db_account[field]

        account._context = context
        account.obj_reset_changes()
        return account

    @classmethod
    def _from_db_objects(cls, context, list_obj):
        return [cls._from_db_object(context, cls(context), obj)
                for obj in list_obj]

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.account_create(context, values))

    @classmethod
    def pay(cls, context, user_id, project_id, order_id, pay_money):
        return cls._from_db_object(
            context,
            cls(),
            db_api.account_pay_money(context,
                                     user_id,
                                     project_id,
                                     order_id,
                                     pay_money))

    @classmethod
    def recharge(cls, context, value):
        return cls._from_db_object(
            context,
            cls(),
            db_api.account_recharge_money(context, value))

    @classmethod
    def get(cls, context, user_id):
        return cls._from_db_object(
            context,
            cls(),
            db_api.account_get(context, user_id))
