from flask import Blueprint, render_template, redirect, url_for, current_app
from flask.ext.security.utils import md5
import os
from realize.log import logging

log = logging.getLogger(__name__)

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(current_app.config['REPO_PATH'], 'templates'))

@main_views.route('/')
def index():
    angular_index = os.path.join("frontend", "index.html")
    angular_path = os.path.join(current_app.config['REPO_PATH'], "static", angular_index)

    # A hack to conditionally render different index pages.
    # Render angular UI if it exists.
    # Hack will be removed at some point.
    if not os.path.isfile(angular_path):
        return render_template("index.html")
    return redirect(url_for('main_views.frontend', filename="index.html"))


## Hacks to get angular frontend working.  Will be removed at some point.
@main_views.route('/frontend/<path:filename>')
def frontend(filename):
    from app import app
    return app.send_static_file(os.path.join("frontend", filename))

@main_views.route('/data/widgetList.json')
def widget_list():
    from app import app
    return app.send_static_file(os.path.join("frontend", "data", "widgetList.json"))

def send_static_file(*args):
    from app import app
    return app.send_static_file(os.path.join(*args))

@main_views.route('/widgets/<path:widget_path>')
def widgets(widget_path):
    return send_static_file("frontend", "widgets", widget_path)

@main_views.route('/assets/<path:asset_path>')
def assets(asset_path):
    return send_static_file("frontend", "assets", asset_path)