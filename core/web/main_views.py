from flask import Blueprint, render_template, abort, request, url_for, jsonify, after_this_request, current_app
from werkzeug.utils import redirect
from core.manager import ExecutionContext
from core.plugins.views import ViewManager
from core.util import append_container, DEFAULT_SECURITY
from realize import settings
import os
from werkzeug.datastructures import MultiDict
from flask.ext.security import login_required, LoginForm, login_user, ConfirmRegisterForm, logout_user
from flask_security.views import _commit, _render_json, anonymous_user_required, register_user
from flask.ext.login import current_user
import json
from core.plugins.lib.forms import JSONMixin
from core.plugins.lib.views import WidgetView
from werkzeug.local import LocalProxy

from flask.views import MethodView

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@main_views.route('/')
def index():
    return render_template("index.html")

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

main_views.add_url_rule('/api/v1/plugins/manage', view_func=ManagePlugins.as_view('manage_plugins'))

class PluginViews(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self):
        from core.plugins.loader import plugins

        user_widgets = []
        for p in current_user.plugins:
            views = plugins[p.hashkey].views
            for v in views:
                context = ExecutionContext(user=current_user, plugin=p)
                manager = ViewManager(context)
                data = manager.get_meta(v.hashkey)
                user_widgets.append(data)

        return jsonify(append_container(user_widgets, name="widgets", tags=[]))

main_views.add_url_rule('/api/v1/views', view_func=PluginViews.as_view('views'))

class JSONLoginForm(LoginForm, JSONMixin):
    pass

@main_views.route('/api/v1/login', methods=["GET", "POST"])
@anonymous_user_required
def login():
    """
    View function for login view
    """

    form_class = JSONLoginForm
    if request.json:
        form = form_class(MultiDict(request.json))
    else:
        form = form_class()

    if form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        after_this_request(_commit)

    if request.json:
        return _render_json(form, True)

    return jsonify(form.as_json())

_security = LocalProxy(lambda: current_app.extensions['security'])

class JSONRegisterForm(ConfirmRegisterForm, JSONMixin):
    pass

@main_views.route('/api/v1/register', methods=["GET", "POST"])
@anonymous_user_required
def register():
    """
    View function which handles a registration request.
    """
    form_class = JSONRegisterForm
    form = form_class(MultiDict(request.json))

    if form.validate_on_submit():
        user = register_user(**form.to_dict())
        form.user = user

        if not _security.confirmable or _security.login_without_confirmation:
            after_this_request(_commit)
            login_user(user)

        return _render_json(form, True)

    return jsonify(form.as_json())

@main_views.route('/api/v1/logout', methods=["GET", "POST"])
def logout():
    """
    View function which handles a logout request.
    """

    if current_user.is_authenticated():
        logout_user()

    return jsonify({'status': 200})