from flask import Blueprint, render_template, abort, request, jsonify
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import url_for
from flask.views import MethodView
from core.database.models import ResourceData
from core.resources.manager import ResourceManager
from core.util import DEFAULT_SECURITY, append_container, get_context_for_scope, api_url_for
from realize import settings
import os
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

from realize.log import logging
log = logging.getLogger(__name__)

resource_views = Blueprint('resource_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
api = swagger.docs(Api(resource_views), api_spec_url=settings.API_SPEC_URL)

class BaseResourceView(Resource):
    method_decorators = [DEFAULT_SECURITY]

    def convert(self, resource):
        return dict(
            hashkey=resource.hashkey,
            name=resource.name,
            type=resource.type,
            settings=resource.settings
        )

class ResourceView(BaseResourceView):
    method_decorators = [DEFAULT_SECURITY]

    def get(self, scope, hashkey):
        from app import db
        context, mod = get_context_for_scope(scope, hashkey)
        resource_data = db.session.query(ResourceData).filter(getattr(ResourceData, scope) == mod).all()
        resources = []
        for r in resource_data:
            data = self.convert(r)
            print data
            url = api_url_for("resource_views", ResourceDetail, resource_hashkey=data['hashkey'], scope=scope, hashkey=hashkey)
            data['url'] = url
            resources.append(data)
        return resources

    def post(self, scope, hashkey):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='The name of the resource.')
        parser.add_argument('type', type=str, help='The type of the resource.')
        parser.add_argument('settings', type=dict, help='Settings to store.')
        args = parser.parse_args()

        name = args['name']
        type = args['type']
        settings = args['settings']

        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model = manager.create_resource(settings, name, type)
        return self.convert(model)

api.add_resource(ResourceView, '/api/v1/<string:scope>/<string:hashkey>/resources')

class ResourceDetail(BaseResourceView):

    def get(self, scope, hashkey, resource_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model, model_settings = manager.get_resource(resource_hashkey)
        return model_settings

    def delete(self, scope, hashkey, resource_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        manager.delete_resource(resource_hashkey)
        return {}, 204

    def put(self, scope, hashkey, resource_hashkey):
        settings = request.json['settings']
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        manager.update_resource(resource_hashkey, settings)
        return {}

api.add_resource(ResourceDetail, '/api/v1/<string:scope>/<string:hashkey>/resources/<string:resource_hashkey>')
