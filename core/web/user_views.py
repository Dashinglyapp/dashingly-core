from flask import Blueprint, request, jsonify
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask_wtf import Form
from flask.views import MethodView
from wtforms import TextField
from wtforms_json import MultiDict
from core.plugins.lib.views.forms import JSONMixin
from core.util import DEFAULT_SECURITY, append_container
from realize import settings
import os
from realize.log import logging
import json
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

log = logging.getLogger(__name__)

user_views = Blueprint('user_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
api = swagger.docs(Api(user_views), api_spec_url=settings.API_SPEC_URL)

class UserProfileForm(Form, JSONMixin):
    first_name = TextField('First Name', description="Your first name.")
    last_name = TextField('Last Name', description="Your last name.")
    settings = TextField('Settings', description="Settings.")
    timezone = TextField('Timezone', description="Your timezone.")

class UserProfile(Resource):
    decorators = [DEFAULT_SECURITY]
    fields = ["first_name", "last_name", "settings", "timezone"]

    def get_model(self):
        model = current_user.profile
        data = {
            'first_name': model.first_name,
            'last_name': model.last_name,
            'settings': model.settings,
            'timezone': model.timezone,
            'hashkey': current_user.hashkey,
        }
        try:
            data['settings'] = json.loads(data['settings'])
        except ValueError:
            data['settings'] = {}
        except TypeError:
            data['settings'] = {}
        form = UserProfileForm(**data)
        return model, form.as_json()

    def get(self, hashkey):
        model, data = self.get_model()
        return data

    def post(self, hashkey):
        from app import db
        model, model_settings = self.get_model()
        for attr in self.fields:
            if hasattr(request, "json") and attr in request.json:
                val = request.json.get(attr, model)
                if attr == "settings":
                    val = json.dumps(val)
                setattr(model, attr, val)
        db.session.commit()
        return {}, 201

api.add_resource(UserProfile, '/api/v1/user/<string:hashkey>/profile')
