from flask import jsonify, request, Blueprint
from flask.views import MethodView
from core.database.models import Group
from core.util import DEFAULT_SECURITY, append_container
from flask.ext.login import current_user
from flask.ext.security import login_required
from realize import settings
import os
from realize.log import logging
import json

log = logging.getLogger(__name__)
group_views = Blueprint('group_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

class InvalidActionException(Exception):
    pass

class BaseGroupView(MethodView):
    decorators = [DEFAULT_SECURITY]
    fields = ["name", "description"]

    def convert_group(self, group):
        data = {
            'name': group.name,
            'description': group.description,
            'owner': current_user == group.owner
        }
        return data

    def get_group_by_key(self, hashkey):
        return Group.query.filter(Group.hashkey == hashkey).first()

class GroupView(BaseGroupView):

    def get(self):
        data = []
        for g in Group.query.all():
            data.append(self.convert_group(g))
        return jsonify(append_container(data, name="user_groups"))

    def post(self):
        from app import db
        mod = Group.query.filter(Group.owner == current_user).first()
        if mod is None:
            mod = Group(owner=current_user)
            for attr in self.fields:
                if hasattr(request, "json") and attr in request.json:
                    val = request.json.get(attr, mod)
                    setattr(mod, attr, val)
            current_user.groups.append(mod)
            db.session.commit()
        return jsonify(append_container("", code=201))

group_views.add_url_rule('/api/v1/group', view_func=GroupView.as_view('groups'))

class GroupDetailView(BaseGroupView):

    def get(self, hashkey):
        mod = self.get_group_by_key(hashkey)
        return jsonify(append_container(self.convert_group(mod), name="user_groups"))

group_views.add_url_rule('/api/v1/group/<string:hashkey>', view_func=GroupDetailView.as_view('group_detail'))

class UserGroupView(BaseGroupView):
    def get(self):
        data = []
        for g in current_user.groups:
            data.append(self.convert_group(g))
        return jsonify(append_container(data, name="user_groups"))

group_views.add_url_rule('/api/v1/user/<string:user_hashkey>/groups', view_func=GroupDetailView.as_view('user_group_view'))

class UserGroupActionView(BaseGroupView):

    def add(self, hashkey):
        from app import db
        mod = self.get_group_by_key(hashkey)
        current_user.groups.append(mod)
        db.session.commit()

    def remove(self, hashkey):
        from app import db
        mod = self.get_group_by_key(hashkey)
        current_user.groups.remove(mod)
        db.session.commit()

    def get(self, user_hashkey, group_hashkey, action):
        if action == "add":
            data = self.add(group_hashkey)
        elif action == "remove":
            data = self.remove(group_hashkey)
        else:
            raise InvalidActionException()

        return jsonify(append_container(data, code=201))

group_views.add_url_rule('/api/v1/user/<string:user_hashkey>/groups/<string:group_hashkey>/<string:action>', view_func=UserGroupActionView.as_view('user_group_actions'))
