from flask import Blueprint, render_template, request, jsonify, after_this_request, current_app
from flask.ext.security.utils import md5
from app import csrf
from wtforms_json import MultiDict
from core.util import append_container
from realize import settings
import os
from flask.ext.security import login_required, LoginForm, login_user, ConfirmRegisterForm, logout_user
from flask_security.views import _commit, register_user
from flask.ext.login import current_user
from core.plugins.lib.views.forms import JSONMixin
from werkzeug.local import LocalProxy
from realize.log import logging

log = logging.getLogger(__name__)

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

def authentication_response(form):
    has_errors = len(form.errors) > 0

    if has_errors:
        code = 400
        response = dict(errors=form.errors)
    else:
        code = 200
        response = dict(
            user=dict(
                id=str(form.user.id),
                hashkey=form.user.hashkey,
                token=form.user.get_auth_token()
            ))

    return jsonify(append_container(response, code=code))

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

        return authentication_response(form)

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

        return authentication_response(form)

    return jsonify(form.as_json())

@main_views.route('/api/v1/logout', methods=["GET", "POST"])
def logout():
    """
    View function which handles a logout request.
    """

    if current_user.is_authenticated():
        logout_user()

    return jsonify({'status': 200})


def check_token(token):
    try:
        data = current_app.extensions['security'].remember_token_serializer.loads(token, max_age=settings.MAX_TOKEN_AGE)
        user = current_app.extensions['security'].datastore.find_user(id=data[0])
        if user and md5(user.password) == data[1]:
            return user
    except Exception:
        pass
    return None

@main_views.route('/api/v1/auth_check', methods=["GET", "POST"])
@csrf.exempt
def authentication_check():
    """
    View function to check authentication status.
    """
    from app import token_loader

    token = request.json['token']
    user = check_token(token)
    authenticated = user is not None
    data = dict(authenticated=authenticated)
    if authenticated:
        data.update(dict(
            email=current_user.email,
            hashkey=current_user.hashkey,
            id=current_user.id,
        ))
    return jsonify(append_container(data, data_key="auth_info"))

