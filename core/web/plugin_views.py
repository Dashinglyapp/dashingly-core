from flask import Blueprint, render_template, abort, request, jsonify
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from flask.views import MethodView
from wtforms_json import MultiDict
from core.database.models import Group
from core.manager import ExecutionContext
from core.plugins.views import ViewManager
from core.util import DEFAULT_SECURITY, append_container, get_context_for_scope, InvalidScopeException
from core.web.group_views import InvalidActionException
from realize import settings
import os
from core.plugins.manager import PluginManager, PluginActionRunner
from core.plugins.lib.proxies import PluginProxy
from realize.log import logging
log = logging.getLogger(__name__)

plugin_views = Blueprint('plugin_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

class PluginList(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self, scope, hashkey):
        from core.plugins.loader import plugins
        context, model = get_context_for_scope(scope, hashkey)
        installed_plugins = model.plugins
        installed_keys = [p.hashkey for p in installed_plugins]

        plugin_schema = []
        for p in plugins:
            plugin = plugins[p]
            plugin_scheme = dict(
                name=plugin.name,
                description=plugin.description,
                remove_url=url_for('plugin_views.plugin_detail', plugin_hashkey=plugin.hashkey, scope=scope, hashkey=hashkey, action="remove"),
                configure_url=url_for('plugin_views.plugin_detail', plugin_hashkey=plugin.hashkey, scope=scope, hashkey=hashkey, action="configure"),
                add_url=url_for('plugin_views.plugin_detail', plugin_hashkey=plugin.hashkey, scope=scope, hashkey=hashkey, action="add"),
                installed=(plugin.hashkey in installed_keys)
            )
            plugin_schema.append(plugin_scheme)

        return jsonify(append_container(plugin_schema, name="plugin_list", tags=["system"]))

plugin_views.add_url_rule('/api/v1/<string:scope>/<string:hashkey>/plugins', view_func=PluginList.as_view('plugin_list'))

class PluginDetailView(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get_runner(self, scope, hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        runner = PluginActionRunner(context)
        return runner

    def get_task_url(self, task_id):
        if task_id is not None:
            return url_for('task_views.task_status', task_id=task_id)
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
        response = runner.save_settings(plugin_hashkey, MultiDict(request.json))
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

        return jsonify(append_container(data, code=201))

    def post(self, scope, hashkey, plugin_hashkey, action):
        if action == "configure":
            data = self.save_settings(scope, hashkey, plugin_hashkey)
        else:
            raise InvalidActionException()

        return jsonify(append_container(data, code=201))

plugin_views.add_url_rule('/api/v1/<string:scope>/<string:hashkey>/plugins/<string:plugin_hashkey>/actions/<string:action>', view_func=PluginDetailView.as_view('plugin_detail'))

class PluginViewsList(MethodView):
    decorators = [DEFAULT_SECURITY]

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
                user_views.append(data)

        return jsonify(append_container(user_views, name="views", tags=[]))

plugin_views.add_url_rule('/api/v1/<string:scope>/<string:hashkey>/views', view_func=PluginViewsList.as_view('plugin_views'))

class PluginViewsDetail(MethodView):
    decorators = [DEFAULT_SECURITY]

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
        return manager.call_route_handler(view_hashkey, "post", request.json)

    def put(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "put", request.json)

    def patch(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "patch", request.json)

    def delete(self, scope, hashkey, plugin_hashkey, view_hashkey):
        manager = self.get_manager(scope, hashkey, plugin_hashkey)
        return manager.call_route_handler(view_hashkey, "delete", request.args)

plugin_views.add_url_rule('/api/v1/<string:scope>/<string:hashkey>/plugins/<string:plugin_hashkey>/views/<string:view_hashkey>', view_func=PluginViewsDetail.as_view('plugin_route'))


