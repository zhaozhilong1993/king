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


"""Action object."""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from king.db import api as db_api
from king.objects import base as king_base


class Action(
        king_base.KingObject,
        base.VersionedObjectDictCompat,
        base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'resource_type': fields.StringField(),
        'resource_id': fields.StringField(),
        'user_id': fields.StringField(),
        'project_id': fields.StringField(),
        'action': fields.StringField(),
        'created_at': fields.DateTimeField(),
    }

    @staticmethod
    def _from_db_object(context, action, db_action):
        '''once we finish database action, we need to format the result'''
        for field in action.fields:
            action[field] = db_action[field]

        action._context = context
        action.obj_reset_changes()
        return action

    @classmethod
    def _from_db_objects(cls, context, list_obj):
        return [cls._from_db_object(context, cls(context), obj)
                for obj in list_obj]

    @classmethod
    def get_by_id(cls, context, action_id):
        action_db = db_api.action_get(context, action_id)
        action = cls._from_db_object(context, cls(), action_db)
        return action

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(
            context,
            cls(),
            db_api.action_record(context, values))
