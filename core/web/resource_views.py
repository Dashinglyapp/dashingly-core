from flask import Blueprint, render_template, abort, request, jsonify, current_app
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import url_for
from flask.views import MethodView
from core.database.models import ResourceData
from core.resources.manager import ResourceManager
from core.util import DEFAULT_SECURITY, append_container, get_context_for_scope, api_url_for, get_data
import os
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger
import json

from realize.log import logging
log = logging.getLogger(__name__)

resource_views = Blueprint('resource_views', __name__, template_folder=os.path.join(current_app.config['REPO_PATH'], 'templates'))
api = swagger.docs(Api(resource_views), api_spec_url=current_app.config['API_SPEC_URL'])

class InvalidArgumentsException(Exception):
    pass

class InvalidScopeException(Exception):
    pass

class BaseResourceView(Resource):
    method_decorators = [DEFAULT_SECURITY]
    required_fields = ["name", "type"]

    def get_resource(self, hashkey):
        from app import db
        obj = db.session.query(ResourceData).filter_by(hashkey=hashkey).first()
        return obj

    def convert(self, scope, hashkey, resource, find_related=False):
        if resource.user is not None:
            owner_key = resource.user.hashkey
            res_scope = "user"
        elif resource.group is not None:
            owner_key = resource.group.hashkey
            res_scope = "group"
        else:
            raise InvalidScopeException()
        permissions = []
        for p in resource.permissions:
            if p.user is not None:
                key = p.user.hashkey
            elif p.group is not None:
                key = p.group.hashkey
            else:
                key = None
            permissions.append(dict(
                public=p.public,
                hashkey=key,
                scope=p.scope
            ))
        vals = dict(
            hashkey=resource.hashkey,
            name=resource.name,
            type=resource.type,
            settings=resource.settings,
            owner_scope=res_scope,
            owner_hashkey=owner_key,
            views=[v.hashkey for v in resource.views],
            permissions=permissions,
            current_view=resource.current_view
        )
        if find_related:
            related = []
            context, mod = get_context_for_scope(scope, hashkey)
            manager = ResourceManager(context)
            for r in resource.related:
                if manager.check_permissions(r, "view"):
                    related.append(r)
            vals['related'] = [self.convert(scope, hashkey, r, find_related=find_related) for r in related]
        return vals

    def make_model(self, scope, hashkey, **kwargs):
        from app import db
        for arg in self.required_fields:
            if arg not in kwargs:
                raise InvalidArgumentsException()

        parent = kwargs.pop('parent', None)

        if 'settings' in kwargs:
            try:
                kwargs['settings'] = json.loads(kwargs['settings'])
            except Exception:
                pass

        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model = manager.create_resource(**kwargs)

        # If the resource specifies its parent, then automatically setup the link.
        if parent:
            parent_model = self.get_resource(parent)
            if parent_model:
                parent_model.related.append(model)
                db.session.commit()
        return model


class ResourceView(BaseResourceView):

    def get(self, scope, hashkey):
        from app import db
        context, mod = get_context_for_scope(scope, hashkey)
        resource_data = db.session.query(ResourceData).filter(getattr(ResourceData, scope) == mod).all()
        resources = []
        for r in resource_data:
            data = self.convert(scope, hashkey, r)
            url = api_url_for("resource_views", ResourceDetail, resource_hashkey=data['hashkey'], scope=scope, hashkey=hashkey)
            data['url'] = url
            resources.append(data)
        return resources

    @swagger.operation(
            parameters=[
                {
                    "name": "name",
                    "description": "Name of the resource.",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                },
                {
                    "name": "type",
                    "description": "Type of the resource.",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                },
                {
                    "name": "settings",
                    "description": "Settings to store.",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                },
                ])

    def post(self, scope, hashkey):
        data = get_data()

        return self.convert(scope, hashkey, self.make_model(scope, hashkey, **data))

api.add_resource(ResourceView, '/api/v1/<string:scope>/<string:hashkey>/resources')

class TreeResourceView(BaseResourceView):

    def process_related(self, scope, hashkey, data):
        from app import db
        related = data.pop('related', None)
        root = self.make_model(scope, hashkey, **data)
        if related is not None:
            try:
                related = json.loads(related)
            except:
                pass

            for r in related:
                model = self.process_related(scope, hashkey, r)
                root.related.append(model)
        db.session.commit()
        return root

    def post(self, scope, hashkey):
        data = get_data()
        root = self.process_related(scope, hashkey, data)
        return self.convert(scope, hashkey, root, find_related=True)

api.add_resource(TreeResourceView, '/api/v1/<string:scope>/<string:hashkey>/resources/tree')

class ResourceDetail(BaseResourceView):

    def get(self, scope, hashkey, resource_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model, model_settings = manager.get_resource(resource_hashkey)
        return self.convert(scope, hashkey, model)

    def delete(self, scope, hashkey, resource_hashkey):
        from app import db
        parent = request.args.get('parent', None)
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        manager.delete_resource(resource_hashkey)
        if parent:
            parent_model = self.get_resource(parent)
            if parent_model:
                parent_model.related.remove()
                db.session.commit()
        return {}


    @swagger.operation(
            parameters=[
                {
                    "name": "name",
                    "description": "Name of the resource.",
                    "required": False,
                    "dataType": "string",
                    "paramType": "string"
                },
                {
                    "name": "type",
                    "description": "Type of the resource.",
                    "required": False,
                    "dataType": "string",
                    "paramType": "string"
                },
                {
                    "name": "settings",
                    "description": "Settings to store.",
                    "required": False,
                    "dataType": "string",
                    "paramType": "string"
                },
                ])

    def patch(self, scope, hashkey, resource_hashkey):
        settings = get_data()
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model = manager.update_resource(resource_hashkey, settings)
        return self.convert(scope, hashkey, model)

api.add_resource(ResourceDetail, '/api/v1/<string:scope>/<string:hashkey>/resources/<string:resource_hashkey>')

class TreeResourceDetail(BaseResourceView):

    def get(self, scope, hashkey, resource_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        manager = ResourceManager(context)
        model, model_settings = manager.get_resource(resource_hashkey)
        return self.convert(scope, hashkey, model, find_related=True)

api.add_resource(TreeResourceDetail, '/api/v1/<string:scope>/<string:hashkey>/resources/<string:resource_hashkey>/tree')