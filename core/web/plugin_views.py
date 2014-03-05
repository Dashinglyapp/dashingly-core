from flask import Blueprint, render_template, abort, request, jsonify
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from flask.views import MethodView
from core.manager import ExecutionContext
from core.plugins.views import ViewManager
from core.util import DEFAULT_SECURITY, append_container
from realize import settings
import os
from core.plugins.manager import PluginManager
from core.plugins.lib.proxies import PluginProxy
from realize.log import logging
log = logging.getLogger(__name__)

plugin_views = Blueprint('plugin_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@plugin_views.route('/api/v1/plugins/<plugin_hashkey>/actions/add')
@DEFAULT_SECURITY
def add(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.add(plugin_hashkey)
    return jsonify(append_container({}, code=200))

@plugin_views.route('/api/v1/plugins/<plugin_hashkey>/actions/remove')
@DEFAULT_SECURITY
def remove(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.remove(plugin_hashkey)
    return jsonify(append_container({}, code=200))

@plugin_views.route('/api/v1/plugins/<plugin_hashkey>/actions/configure')
@DEFAULT_SECURITY
def configure(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    return manager.get_settings(plugin_hashkey, request.form)

class PluginRoute(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get_manager(self, plugin_hashkey):
        context = ExecutionContext(user=current_user, plugin=PluginProxy(hashkey=plugin_hashkey, name=""))
        manager = PluginManager(context)
        return manager

    def get(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        val = manager.call_route_handler(plugin_route, "get", request.args)
        return val

    def post(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "post", request.json)

    def put(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "put", request.json)

    def patch(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "patch", request.json)

    def delete(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "delete", request.args)

plugin_views.add_url_rule('/api/v1/plugins/<string:plugin_hashkey>/<path:plugin_route>', view_func=PluginRoute.as_view('plugin_route'))

class ManagePlugins(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self):
        from core.plugins.loader import plugins
        installed_plugins = current_user.plugins
        installed_keys = [p.hashkey for p in installed_plugins]

        plugin_schema = []
        for p in plugins:
            plugin = plugins[p]
            plugin_scheme = dict(
                name=plugin.name,
                description=plugin.description,
                remove_url=url_for('plugin_views.remove', plugin_hashkey=plugin.hashkey),
                configure_url=url_for('plugin_views.configure', plugin_hashkey=plugin.hashkey),
                add_url=url_for('plugin_views.add', plugin_hashkey=plugin.hashkey),
                installed=(plugin.hashkey in installed_keys)
            )
            plugin_schema.append(plugin_scheme)

        return jsonify(append_container(plugin_schema, name="plugin_list", tags=["system"]))

plugin_views.add_url_rule('/api/v1/plugins/manage', view_func=ManagePlugins.as_view('manage_plugins'))

class PluginViews(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self):
        from core.plugins.loader import plugins

        user_views = []
        for p in current_user.plugins:
            views = plugins[p.hashkey].views
            for v in views:
                context = ExecutionContext(user=current_user, plugin=p)
                manager = ViewManager(context)
                data = manager.get_meta(v.hashkey)
                user_views.append(data)

        return jsonify(append_container(user_views, name="views", tags=[]))

plugin_views.add_url_rule('/api/v1/views', view_func=PluginViews.as_view('views'))


