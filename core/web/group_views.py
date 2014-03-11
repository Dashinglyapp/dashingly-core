from flask import jsonify, request, Blueprint
from flask.views import MethodView
from core.database.models import Group
from core.groups.permissions import GroupPermissions
from core.manager import ExecutionContext
from core.util import DEFAULT_SECURITY, append_container, get_data
from flask.ext.login import current_user
from flask.ext.security import login_required
from realize import settings
import os
from realize.log import logging
import json
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

log = logging.getLogger(__name__)
group_views = Blueprint('group_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
api = swagger.docs(Api(group_views), api_spec_url=settings.API_SPEC_URL)

class InvalidActionException(Exception):
    pass

class BaseGroupView(Resource):
    decorators = [DEFAULT_SECURITY]
    fields = ["name", "description"]

    def convert_group(self, group):
        data = {
            'name': group.name,
            'description': group.description,
            'owner': current_user == group.owner,
            'hashkey': group.hashkey
        }
        return data

    def get_group_by_key(self, hashkey):
        return Group.query.filter(Group.hashkey == hashkey).first()

group_parser = reqparse.RequestParser()
group_parser.add_argument('name', type=str, help='The name of the group.')
group_parser.add_argument('description', type=str, help='The description of the group.')

class GroupView(BaseGroupView):
    """
    Shows what groups are available and makes new ones.
    GET will return a list of groups.  Returns name, description, owner, and hashkey.
    """

    def get(self):
        data = []
        for g in Group.query.all():
            data.append(self.convert_group(g))
        return data

    @swagger.operation(
            parameters=[
                {
                    "name": "name",
                    "description": "Name of the group.",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                },
                {
                    "name": "description",
                    "description": "Group description.",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                },
            ])

    def post(self):
        from app import db
        args = group_parser.parse_args()

        mod = Group(owner=current_user)
        mod.name = args['name']
        mod.description = args['description']
        current_user.groups.append(mod)
        db.session.commit()
        return self.convert_group(mod), 201

api.add_resource(GroupView, '/api/v1/group')

class GroupDetailView(BaseGroupView):

    def get(self, hashkey):
        mod = self.get_group_by_key(hashkey)
        return self.convert_group(mod)

    @swagger.operation(
            parameters=[
                {
                    "name": "description",
                    "description": "Group description.",
                    "required": False,
                    "dataType": "string",
                    "paramType": "string"
                },
                ])

    def put(self, hashkey):
        from app import db
        mod = self.get_group_by_key(hashkey)
        context = ExecutionContext(user=current_user)
        perm_manager = GroupPermissions(context)
        perm = perm_manager.check_perms(mod, "update")
        data = get_data()
        if perm:
            mod.description = data.get('description', mod.description)
            db.session.commit()
        return self.convert_group(mod), 200

api.add_resource(GroupDetailView, '/api/v1/group/<string:hashkey>')

class UserGroupView(BaseGroupView):
    def get(self, user_hashkey):
        data = []
        for g in current_user.groups:
            data.append(self.convert_group(g))
        return data

api.add_resource(UserGroupView, '/api/v1/user/<string:user_hashkey>/groups')

class UserGroupActionView(BaseGroupView):

    def add(self, hashkey):
        from app import db
        mod = self.get_group_by_key(hashkey)
        current_user.groups.append(mod)
        db.session.commit()
        return self.convert_group(mod), 200

    def remove(self, hashkey):
        from app import db
        mod = self.get_group_by_key(hashkey)
        current_user.groups.remove(mod)
        db.session.commit()
        return {}, 200

    def get(self, user_hashkey, group_hashkey, action):
        if action == "add":
            data = self.add(group_hashkey)
        elif action == "remove":
            data = self.remove(group_hashkey)
        else:
            raise InvalidActionException()

        return data

api.add_resource(UserGroupActionView, '/api/v1/user/<string:user_hashkey>/groups/<string:group_hashkey>/<string:action>')
