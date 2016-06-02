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


"""Service object."""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from king.db import api as db_api
from king.objects import base as king_base


class Valume(
        king_base.KingObject,
        base.VersionedObjectDictCompat,
        base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'user_id': fields.StringField(),
        'valume_num': fields.IntegerField(),
        'valume_size': fields.StringField(),
        'created_at': fields.DateTimeField(read_only=True),
        'updated_at': fields.DateTimeField(nullable=True),
        'deleted_at': fields.DateTimeField(nullable=True)
    }

    @staticmethod
    def _from_db_object(context, service, db_service):
        '''once we finish database action, we need to format the result'''
        for field in service.fields:
            service[field] = db_service[field]
        service._context = context
        service.obj_reset_changes()
        return service

    @classmethod
    def _from_db_objects(cls, context, list_obj):
        return [cls._from_db_object(context, cls(context), obj)
                for obj in list_obj]

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.valume_create(context, values))

    @classmethod
    def update_by_id(cls, context, user_id, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.valume_update(context, service_id, values))

    @classmethod
    def delete(cls, context, user_id, soft_delete=True):
        db_api.valume_delete(context, service_id, soft_delete)

    @classmethod
    def get_all(cls, context):
        return cls._from_db_objects(context,
                                    db_api.valume_quota_get_all(context))
