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


class Service(
        king_base.KingObject,
        base.VersionedObjectDictCompat,
        base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'engine_id': fields.StringField(),
        'host': fields.StringField(),
        'hostname': fields.StringField(),
        'process': fields.StringField(),
        'topic': fields.StringField(),
        'report_interval': fields.IntegerField(),
        'created_at': fields.DateTimeField(read_only=True),
        'updated_at': fields.DateTimeField(nullable=True),
        'deleted_at': fields.DateTimeField(nullable=True)
    }

    @staticmethod
    def _from_db_object(context, service, db_service):
        '''once we finish database action, we need to format the result'''
        res = {}
        for field in service.fields:
            res[field] = db_service[field]
        return res

    @classmethod
    def _from_db_objects(cls, context, list_obj):
        return [cls._from_db_object(context, cls(context), obj)
                for obj in list_obj]

    @classmethod
    def get_by_id(cls, context, service_id):
        service_db = db_api.service_get(context, service_id)
        service = cls._from_db_object(context, cls(), service_db)
        return service

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.service_create(context, values))

    @classmethod
    def update_by_id(cls, context, service_id, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.service_update(context, service_id, values))

    @classmethod
    def delete(cls, context, service_id, soft_delete=True):
        db_api.service_delete(context, service_id, soft_delete)

    @classmethod
    def get_all(cls, context):
        return cls._from_db_objects(context,
                                    db_api.service_get_all(context))

    @classmethod
    def get_all_by_args(cls, context, host, process, hostname):
        return cls._from_db_objects(
            context,
            db_api.service_get_all_by_args(context,
                                           host,
                                           process,
                                           hostname))
