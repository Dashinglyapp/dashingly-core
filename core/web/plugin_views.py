from flask import Blueprint, render_template, abort, request
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from flask.views import MethodView
from core.manager import ExecutionContext
from core.util import DEFAULT_SECURITY
from realize import settings
import os
from flask import current_app
from core.plugins.manager import PluginManager
from core.plugins.lib.proxies import PluginProxy
from realize.log import logging
log = logging.getLogger(__name__)

plugin_views = Blueprint('plugin_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@plugin_views.route('/plugins/<plugin_hashkey>/actions/add')
@DEFAULT_SECURITY
def add(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.add(plugin_hashkey)
    return redirect(url_for('main_views.manage_plugins'))

@plugin_views.route('/plugins/<plugin_hashkey>/actions/remove')
@DEFAULT_SECURITY
def remove(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.remove(plugin_hashkey)
    return redirect(url_for('main_views.manage_plugins'))

@plugin_views.route('/plugins/<plugin_hashkey>/actions/configure')
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

plugin_views.add_url_rule('/plugins/<string:plugin_hashkey>/<path:plugin_route>', view_func=PluginRoute.as_view('plugin_route'))


