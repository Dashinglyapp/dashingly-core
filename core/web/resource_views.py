from flask import Blueprint, render_template, abort, request, jsonify
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import url_for
from flask.views import MethodView
from core.database.models import ResourceData
from core.resources.manager import ResourceManager
from core.util import DEFAULT_SECURITY, append_container, get_context_for_scope
from realize import settings
import os
from realize.log import logging
from app import csrf
log = logging.getLogger(__name__)

resource_views = Blueprint('resource_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

class ResourceView(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self, scope, hashkey):
        from app import db
        context, mod = get_context_for_scope(scope, hashkey)
        resource_data = db.session.query(ResourceData.hashkey).filter(getattr(ResourceData, scope) == mod).all()
        resources = []
        for r in resource_data:
            hashkey = r[0]
            url = url_for('resource_views.resource_detail', resource_hashkey=hashkey, scope=scope, hashkey=hashkey)
            resources.append(dict(hashkey=hashkey, url=url))
        return jsonify(append_container(resources, code=200))

    @csrf.exempt
    def post(self, scope, hashkey):
        name = request.json['name']
        type = request.json['type']
        settings = request.json['settings']

        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model = manager.create_resource(settings, name, type)
        return jsonify(append_container({'hashkey': model.hashkey}, code=201, name="model"))

resource_views.add_url_rule('/api/v1/<string:scope>/<string:hashkey>/resources', view_func=ResourceView.as_view('resources'))

class ResourceDetail(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self, scope, hashkey, resource_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model, model_settings = manager.get_resource(resource_hashkey)
        return jsonify(append_container(model_settings, name="resource_data", data_key='data'))

    def delete(self, scope, hashkey, resource_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        manager.delete_resource(resource_hashkey)
        return jsonify(append_container("", code=204))

    def put(self, scope, hashkey, resource_hashkey):
        settings = request.json['settings']
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        manager.update_resource(resource_hashkey, settings)

resource_views.add_url_rule('/api/v1/<string:scope>/<string:hashkey>/resources/<string:resource_hashkey>', view_func=ResourceDetail.as_view('resource_detail'))
