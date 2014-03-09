from flask import Blueprint, jsonify
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.views import MethodView
from flask_oauthlib.client import OAuth
import os
from core.util import append_container, DEFAULT_SECURITY, get_context_for_scope
from realize import settings
from core.oauth.base import state_token_required, OauthV1Base, OauthV2Base
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

oauth_views = Blueprint('oauth_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
oauth = OAuth(oauth_views)
api = swagger.docs(Api(oauth_views), api_spec_url=settings.API_SPEC_URL)

oauth_handlers = settings.OAUTH_CONFIG.keys()

handlers = {}
login_urls = {}

for handler in oauth_handlers:
    mod = __import__("core.oauth.{0}".format(handler))
    secret_key = "{0}_SECRET".format(handler.upper())
    if not hasattr(settings, secret_key):
        continue

    handler_settings = dict(settings.OAUTH_CONFIG[handler].items() + getattr(settings, secret_key).items())
    handler_obj = oauth.remote_app(
        handler,
        **handler_settings
    )
    authorized_handler = getattr(handler_obj, "authorized_handler")
    token_getter = getattr(handler_obj, "tokengetter")

    authorize_url = '/oauth/{0}/callback'.format(handler)
    login_url = '/oauth/{0}/login'.format(handler)
    auth_route_name = "{0}_authorized".format(handler)
    login_route_name = "{0}_login".format(handler)

    login_urls[handler] = login_url

    for auth in OauthV1Base.__subclasses__() + OauthV2Base.__subclasses__():
        if auth.handler == handler:
            obj = auth(handler_obj, handler_settings)

            login = DEFAULT_SECURITY(getattr(obj, "login"))
            auth_handler = authorized_handler(state_token_required(getattr(obj, "authorized")))
            token = token_getter(getattr(obj, "token"))
            handlers[handler] = handler_obj
            oauth_views.add_url_rule(login_url, login_route_name, view_func=login)
            oauth_views.add_url_rule(authorize_url, auth_route_name, view_func=auth_handler)

class Authorizations(Resource):
    decorators = [DEFAULT_SECURITY]

    def get(self, scope, hashkey):
        context, mod = get_context_for_scope(scope, hashkey)
        auth = mod.authorizations
        current_auth = {}
        for a in auth:
            current_auth[a.name] = auth
        all_logins = login_urls

        auth_schema = []
        for l in all_logins:
            auth_scheme = dict(
                url=all_logins[l],
                name=l,
                active=(l in current_auth)
            )
            auth_schema.append(auth_scheme)

        return auth_schema

api.add_resource(Authorizations, '/api/v1/<string:scope>/<string:hashkey>/authorizations')
