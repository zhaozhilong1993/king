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


"""Order object."""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from king.db import api as db_api
from king.objects import base as king_base


class Order(
        king_base.KingObject,
        base.VersionedObjectDictCompat,
        base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'resource_id': fields.StringField(),
        'project_id': fields.StringField(),
        'price_id': fields.StringField(),
        'order_status': fields.StringField(),
        'order_type': fields.StringField(),
        'deleted_at': fields.DateTimeField(),
        'created_at': fields.DateTimeField(),
        'updated_at': fields.DateTimeField()
    }

    @staticmethod
    def _from_db_object(context, order, db_order):
        '''once we finish database action, we need to format the result'''
        for field in order.fields:
            order[field] = db_order[field]

        order._context = context
        order.obj_reset_changes()
        return order

    @classmethod
    def _from_db_objects(cls, context, list_obj):
        return [cls._from_db_object(context, cls(context), obj)
                for obj in list_obj]

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.order_create(context, values))

    @classmethod
    def get(cls, context, resource_id=None, order_id=None):
        return cls._from_db_object(
            context,
            cls(),
            db_api.order_get(context,
                             resource_id=resource_id,
                             order_id=order_id))

    @classmethod
    def get_all(cls, context, status=None):
        return cls._from_db_objects(
            context,
            db_api.order_get_all(context))

    @classmethod
    def update_status(cls, context, order_id, status):
        return cls._from_db_object(
            context,
            db_api.order_update_status(context, order_id, status))
