from flask import Blueprint, render_template, redirect, url_for, current_app
from flask.ext.security.utils import md5
import os
from realize.log import logging

log = logging.getLogger(__name__)

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(current_app.config['REPO_PATH'], 'templates'))

# Routes to be used in development.  In production, nginx handles this.
if current_app.config['DEBUG']:
    @main_views.route('/')
    def index():
        angular_index = os.path.join("frontend", "app", "index.html")
        angular_path = os.path.join(current_app.config['REPO_PATH'], "static", angular_index)

        # A hack to conditionally render different index pages.
        # Render angular UI if it exists.
        # Hack will be removed at some point.
        if not os.path.isfile(angular_path):
            return render_template("index.html")
        return redirect(url_for('main_views.frontend_index'))



    # Angular routing during development
    @main_views.route('/app')
    def frontend_index():
        from app import app
        return app.send_static_file(os.path.join("frontend", "app", "index.html"))

    @main_views.route('/app/<path:filepath>.<string(minlength=2, maxlength=4):extension>')
    def frontend_files(filepath, extension):
        print "match file {0}".format(filepath)
        from app import app
        return app.send_static_file(os.path.join("frontend", "app", "{0}.{1}".format(filepath, extension)))

    @main_views.route('/app/<path:filepath>')
    def frontend_routes(filepath):
        print "match path {0}".format(filepath)
        from app import app
        return app.send_static_file(os.path.join("frontend", "app", "index.html"))

    # Documentation routes in development
    @main_views.route('/docs/frontend')
    def doc_routes():
        from app import app
        return app.send_static_file(os.path.join("frontend", "docs", "frontend", "index.html"))

    @main_views.route('/docs/<path:filepath>')
    def doc_file_routes(filepath):
        print "match path {0}".format(filepath)
        from app import app
        return app.send_static_file(os.path.join("frontend", "docs", filepath))