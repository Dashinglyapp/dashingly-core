from flask import Blueprint, render_template, abort
from core.metrics.manager import MetricManager
import settings
import os
from flask.ext.security import login_required
from flask.ext.login import current_user

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@main_views.route('/')
def index():
    return render_template("index.html")

@main_views.route('/plugins/list')
@login_required
def manage_plugins():
    from core.plugins.loader import plugins
    from core.plugins.manager import PluginManager
    installed_plugins = PluginManager(current_user).list()
    return render_template("plugins.html", available_plugins=plugins, installed_plugins=[p.hashkey for p in installed_plugins])

@main_views.route('/metrics')
@login_required
def metrics():
    manager = MetricManager(current_user)
    return render_template("metrics.html", installed_metrics=manager.list())
