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


"""Price object."""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from king.db import api as db_api
from king.objects import base as king_base


class Price(
        king_base.KingObject,
        base.VersionedObjectDictCompat,
        base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'resource_type': fields.StringField(),
        'resource_id': fields.StringField(),
        'order_type': fields.StringField(),
        'price_num': fields.FloatField(),
        'deleted_at': fields.DateTimeField(),
        'created_at': fields.DateTimeField(),
        'updated_at': fields.DateTimeField()
    }

    @staticmethod
    def _from_db_object(context, price, db_price):
        '''once we finish database action, we need to format the result'''
        for field in price.fields:
            price[field] = db_price[field]

        price._context = context
        price.obj_reset_changes()
        return price

    @classmethod
    def _from_db_objects(cls, context, list_obj):
        return [cls._from_db_object(context, cls(context), obj)
                for obj in list_obj]

    @classmethod
    def get_by_id(cls, context, price_id):
        price_db = db_api.price_get(context, price_id)
        price = cls._from_db_object(context, cls(), price_db)
        return price

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.price_create(context, values))
