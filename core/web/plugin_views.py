from flask import Blueprint, render_template, abort, request
from flask.ext.restful import Resource, Api
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from core.manager import ExecutionContext
from realize import settings
import os
from flask import current_app
from core.plugins.manager import PluginManager
from core.plugins.proxies import PluginProxy

plugin_views = Blueprint('plugin_views', __name__)
api = Api()
api.init_app(plugin_views)

@plugin_views.route('/plugins/<plugin_hashkey>/add')
@login_required
def add(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.add(plugin_hashkey)
    return redirect(url_for('main_views.manage_plugins'))

@plugin_views.route('/plugins/<plugin_hashkey>/remove')
@login_required
def remove(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.remove(plugin_hashkey)
    current_app.logger.info(current_user.plugins)
    return redirect(url_for('main_views.manage_plugins'))

@plugin_views.route('/plugins/<plugin_hashkey>/configure')
@login_required
def configure(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)

class PluginRoute(Resource):
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
        return manager.call_route_handler(plugin_route, "post", request.form)

    def put(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "put", request.form)

    def patch(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "patch", request.form)

    def delete(self, plugin_hashkey, plugin_route):
        manager = self.get_manager(plugin_hashkey)
        return manager.call_route_handler(plugin_route, "delete", request.args)

api.add_resource(PluginRoute, '/plugins/<string:plugin_hashkey>/<path:plugin_route>')


