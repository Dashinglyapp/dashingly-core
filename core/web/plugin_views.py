from flask import Blueprint, render_template, abort
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from core.manager import ExecutionContext
from realize import settings
import os
from flask import current_app
from core.plugins.manager import PluginManager

plugin_views = Blueprint('plugin_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@plugin_views.route('/plugins/<plugin_hashkey>/add')
@login_required
def add(plugin_hashkey):
    context = ExecutionContext(user=current_user)
    manager = PluginManager(context)
    manager.add(plugin_hashkey)
    current_app.logger.info(current_user.plugins)
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
