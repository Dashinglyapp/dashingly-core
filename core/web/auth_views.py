from flask import Blueprint, render_template, request, jsonify, after_this_request, current_app
from flask.ext.security.utils import md5
from wtforms_json import MultiDict
from core.util import append_container, DEFAULT_SECURITY, get_data
from realize import settings
import os
from flask.ext.security import login_required, LoginForm, login_user, ConfirmRegisterForm, logout_user
from flask_security.views import _commit, register_user
from flask.ext.login import current_user
from core.plugins.lib.views.forms import JSONMixin
from werkzeug.local import LocalProxy
from realize.log import logging
from flask.ext.restful import Resource, Api, marshal_with, reqparse
from flask_restful_swagger import swagger

auth_views = Blueprint('auth_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
api = swagger.docs(Api(auth_views), api_spec_url=settings.API_SPEC_URL)

_security = LocalProxy(lambda: current_app.extensions['security'])

class JSONRegisterForm(ConfirmRegisterForm, JSONMixin):
    pass

class JSONLoginForm(LoginForm, JSONMixin):
    pass

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

    return response, code

def check_token(token):
    try:
        data = current_app.extensions['security'].remember_token_serializer.loads(token, max_age=settings.MAX_TOKEN_AGE)
        user = current_app.extensions['security'].datastore.find_user(id=data[0])
        if user and md5(user.password) == data[1]:
            return user
    except Exception:
        pass
    return None

class Login(Resource):
    """
    Enables the user to login.
    GET will return form data.
    POST returns either the form data with inline errors, or the authentication response, which consists of the user id, hashkey, and token.
    """
    form_class = JSONLoginForm

    def get(self):
        form = self.form_class()

        return form.as_json()

    @swagger.operation(
        parameters=[
            {
                "name": "email",
                "description": "Email for the user.",
                "required": True,
                "dataType": "string",
                "paramType": "string"
            },
            {
                "name": "password",
                "description": "Password for the user",
                "required": True,
                "dataType": "string",
                "paramType": "string"
            }
        ])

    def post(self):
        data = get_data()
        if data is not None:
            form = self.form_class(MultiDict(data))
        else:
            form = self.form_class()

        if form.validate_on_submit():
            login_user(form.user, remember=form.remember.data)
            after_this_request(_commit)

            # This returns the response and the status code.  See function.
            return authentication_response(form)

        return form.as_json(), 400

api.add_resource(Login, '/api/v1/login')

class Register(Resource):
    """
    Enables the user to register.
    GET will return form data.
    POST returns either the form data with inline errors, or the authentication response, which consists of the user id, hashkey, and token.
    """
    form_class = JSONRegisterForm

    def get(self):
        """
        View function which handles a registration request.
        JSON params - token (string)
        Returns - form as json.
        """
        form = self.form_class()

        return form.as_json()


    @swagger.operation(
            parameters=[
                {
                    "name": "email",
                    "description": "Email for the user.",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                },
                {
                    "name": "password",
                    "description": "Password for the user",
                    "required": True,
                    "dataType": "string",
                    "paramType": "string"
                }
            ])

    def post(self):
        """
        Registers a user.
        JSON params - username (string), password (string)
        Returns - form with inline errors if error, authentication response otherwise.
        """
        data = get_data()
        if data is not None:
            form = self.form_class(MultiDict(data))
        else:
            form = self.form_class()

        if form.validate_on_submit():
            user = register_user(**form.to_dict())
            form.user = user

            if not _security.confirmable or _security.login_without_confirmation:
                after_this_request(_commit)
                login_user(user)

            # This returns the response and the status code.  See function.
            return authentication_response(form)

        return form.as_json(), 400

api.add_resource(Register, '/api/v1/register')

class Logout(Resource):
    """
    Logs the user out.
    """
    method_decorators = [DEFAULT_SECURITY]

    def get(self):
        """
        Logs the current user out.
        """
        if current_user.is_authenticated():
            logout_user()

        return {}, 200

api.add_resource(Logout, '/api/v1/logout')

class AuthenticationCheck(Resource):
    """
    Checks if the user is authenticated.
    """

    @swagger.operation(
        parameters=[
            {
                "name": "token",
                "description": "The authentication token to check.",
                "required": True,
                "dataType": "string",
                "paramType": "string"
            }
        ])

    def post(self):
        """
        JSON params - token (string)
        Returns - id, hashkey, email
        """
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str, help='The auth token you want to check.')
        args = parser.parse_args()

        token = args['token']
        user = check_token(token)
        authenticated = user is not None
        data = dict(authenticated=authenticated)
        if authenticated:
            data.update(dict(
                email=user.email,
                hashkey=user.hashkey,
                id=user.id,
                ))
        return data

api.add_resource(AuthenticationCheck, '/api/v1/auth_check')
