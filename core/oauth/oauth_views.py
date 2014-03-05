from flask import Blueprint, jsonify
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.views import MethodView
from flask_oauthlib.client import OAuth
import os
from core.util import append_container, DEFAULT_SECURITY
from realize import settings
from core.oauth.base import OauthBase, state_token_required

oauth_views = Blueprint('oauth_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
oauth = OAuth(oauth_views)

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

    for auth in OauthBase.__subclasses__():
        if auth.handler == handler:
            obj = auth(handler_obj)

            login = DEFAULT_SECURITY(getattr(obj, "login"))
            auth_handler = authorized_handler(state_token_required(getattr(obj, "authorized")))
            token = token_getter(getattr(obj, "token"))
            handlers[handler] = handler_obj
            oauth_views.add_url_rule(login_url, login_route_name, view_func=login)
            oauth_views.add_url_rule(authorize_url, auth_route_name, view_func=auth_handler)

class Authorizations(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get(self):
        auth = current_user.authorizations
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

        return jsonify(append_container(auth_schema, name="authorizations", tags=["system"]))

oauth_views.add_url_rule('/api/v1/authorizations', view_func=Authorizations.as_view('authorizations'))
