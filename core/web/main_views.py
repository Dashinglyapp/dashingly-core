from flask import Blueprint, render_template, request, jsonify, after_this_request, current_app
from wtforms_json import MultiDict
from realize import settings
import os
from flask.ext.security import login_required, LoginForm, login_user, ConfirmRegisterForm, logout_user
from flask_security.views import _commit, _render_json, register_user
from flask.ext.login import current_user
from core.plugins.lib.views.forms import JSONMixin
from werkzeug.local import LocalProxy

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@main_views.route('/')
def index():
    return render_template("index.html")

class JSONLoginForm(LoginForm, JSONMixin):
    pass

@main_views.route('/api/v1/login', methods=["GET", "POST"])
def login():
    """
    View function for login view
    """

    form_class = JSONLoginForm
    if hasattr(request, 'json') and request.json is not None:
        form = form_class(MultiDict(request.json))
    else:
        form = form_class()

    if form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        after_this_request(_commit)

        return _render_json(form, True)

    return jsonify(form.as_json())

_security = LocalProxy(lambda: current_app.extensions['security'])

class JSONRegisterForm(ConfirmRegisterForm, JSONMixin):
    pass

@main_views.route('/api/v1/register', methods=["GET", "POST"])
def register():
    """
    View function which handles a registration request.
    """
    form_class = JSONRegisterForm
    if hasattr(request, 'json') and request.json is not None:
        form = form_class(MultiDict(request.json))
    else:
        form = form_class()

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