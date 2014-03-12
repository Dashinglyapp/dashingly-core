from flask import Blueprint, render_template, abort, request, jsonify, current_app
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from flask.views import MethodView
from wtforms_json import MultiDict
from core.database.models import Group
from core.manager import ExecutionContext
from core.oauth.manager import AuthorizationManager
from core.plugins.views import ViewManager
from core.util import DEFAULT_SECURITY, append_container, get_context_for_scope, InvalidScopeException, api_url_for, get_data
from core.web.group_views import InvalidActionException
from realize import settings
import os
from core.plugins.manager import PluginManager, PluginActionRunner
from core.plugins.lib.proxies import PluginProxy
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger
from realize.log import logging

log = logging.getLogger(__name__)

plugin_views = Blueprint('plugin_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
api = swagger.docs(Api(plugin_views), api_spec_url=settings.API_SPEC_URL)

class BasePluginView(Resource):
    method_decorators = [DEFAULT_SECURITY]

    def convert(self, plugin, scope, hashkey):
        data = self.base_convert(plugin)
        data.update(dict(
            remove_url=api_url_for("plugin_views", PluginActionView, plugin_hashkey=plugin.hashkey, scope=scope, hashkey=hashkey, action="remove"),
            configure_url=api_url_for("plugin_views", PluginActionView, plugin_hashkey=plugin.hashkey, scope=scope, hashkey=hashkey, action="configure"),
            add_url=api_url_for("plugin_views", PluginActionView, plugin_hashkey=plugin.hashkey, scope=scope, hashkey=hashkey, action="add")
        ))
        return data

    def base_convert(self, plugin):
        context = ExecutionContext(plugin=plugin)
        data = dict(
            name=plugin.name,
            description=plugin.description,
            permissions=AuthorizationManager(context).get_permissions(),
            hashkey=plugin.hashkey
        )
        return data

    def get_group_by_key(self, hashkey):
        return Group.query.filter(Group.hashkey == hashkey).first()

    def get_base_list(self, plugins):
        plugin_schema = []
        for p in plugins:
            plugin = plugins[p]
            plugin_scheme = self.base_convert(plugin)
            plugin_schema.append(plugin_scheme)

        return plugin_schema

    def get_url(self, scope, hashkey, plugin_key, view_key):
            return api_url_for(
                'plugin_views',
                PluginViewsDetail,
                scope=scope,
                hashkey=hashkey,
                plugin_hashkey=plugin_key,
                view_hashkey=view_key
            )

class ScopePluginList(BasePluginView):

    def get(self, scope, hashkey):
        from core.plugins.loader import plugins
        context, model = get_context_for_scope(scope, hashkey)
        installed_plugins = model.plugins
        installed_keys = [p.hashkey for p in installed_plugins]

        plugin_schema = []
        for p in plugins:
            plugin = plugins[p]
            plugin_scheme = self.convert(plugin, scope, hashkey)
            plugin_scheme['installed'] = (plugin.hashkey in installed_keys)
            plugin_schema.append(plugin_scheme)

        return plugin_schema

api.add_resource(ScopePluginList, '/api/v1/<string:scope>/<string:hashkey>/plugins')

class PluginActionView(BasePluginView):

    def get_runner(self, scope, hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        runner = PluginActionRunner(context)
        return runner

    def get_task_url(self, task_id):
        from core.tasks.task_views import TaskStatus
        if task_id is not None:
            return api_url_for('task_views', TaskStatus,  task_id=task_id)
        return None

    def add(self, scope, hashkey, plugin_hashkey):
        runner = self.get_runner(scope, hashkey)
        data = runner.add(plugin_hashkey)
        data['url'] = self.get_task_url(data['task_id'])
        return data

    def remove(self, scope, hashkey, plugin_hashkey):
        runner = self.get_runner(scope, hashkey)
        data = runner.remove(plugin_hashkey)
        data['url'] = self.get_task_url(data['task_id'])
        return data

    def get_settings(self, scope, hashkey, plugin_hashkey):
        runner = self.get_runner(scope, hashkey)
        response = runner.get_settings(plugin_hashkey)
        return response

    def save_settings(self, scope, hashkey, plugin_hashkey):
        runner = self.get_runner(scope, hashkey)
        response = runner.save_settings(plugin_hashkey, MultiDict(get_data()))
        return response

    def get(self, scope, hashkey, plugin_hashkey, action):
        if action == "add":
            data = self.add(scope, hashkey, plugin_hashkey)
        elif action == "remove":
            data = self.remove(scope, hashkey, plugin_hashkey)
        elif action == "configure":
            data = self.get_settings(scope, hashkey, plugin_hashkey)
        else:
            raise InvalidActionException()

        return data

    def post(self, scope, hashkey, plugin_hashkey, action):
        if action == "configure":
            data = self.save_settings(scope, hashkey, plugin_hashkey)
        else:
            raise InvalidActionException()

        return data

api.add_resource(PluginActionView, '/api/v1/<string:scope>/<string:hashkey>/plugins/<string:plugin_hashkey>/actions/<string:action>')

class ScopeViewsList(BasePluginView):

    def get(self, scope, hashkey):
        from core.plugins.loader import plugins
        context, mod = get_context_for_scope(scope, hashkey)
        user_views = []
        for p in mod.plugins:
            views = plugins[p.hashkey].views
            for v in views:
                context.plugin = p
                manager = ViewManager(context)
                data = manager.get_meta(v.hashkey)
                data['url'] = self.get_url(scope, hashkey, p.hashkey, v.hashkey)
                user_views.append(data)

        return user_views

api.add_resource(ScopeViewsList, '/api/v1/<string:scope>/<string:hashkey>/views')

class PluginViewsList(BasePluginView):

    def get(self, scope, hashkey, plugin_hashkey):
        from core.plugins.loader import plugins
        context, mod = get_context_for_scope(scope, hashkey)
        views = plugins[plugin_hashkey].views

        context.plugin = plugins[plugin_hashkey]
        manager = ViewManager(context)
        user_views = []
        for v in views:
            data = manager.get_meta(v.hashkey)
            data['url'] = self.get_url(scope, hashkey, plugin_hashkey, v.hashkey)
            user_views.append(data)
        return user_views

api.add_resource(PluginViewsList, '/api/v1/<string:scope>/<string:hashkey>/plugins/<string:plugin_hashkey>/views')

class PluginViewsDetail(BasePluginView):

    def get_manager(self, scope, hashkey, plugin_hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        context.plugin = PluginProxy(hashkey=plugin_hashkey, name="")
        manager = PluginManager(context)
        return manager

    def get(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        val = manager.call_route_handler(view_hashkey, "get", request.args)
        return val

    def post(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "post", get_data())

    def put(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "put", get_data())

    def patch(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "patch", get_data())

    def delete(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "delete", request.args)

api.add_resource(PluginViewsDetail, '/api/v1/<string:scope>/<string:hashkey>/plugins/<string:plugin_hashkey>/views/<string:view_hashkey>')