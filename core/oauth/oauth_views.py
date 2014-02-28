from flask import Blueprint,  request, url_for, session, render_template
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask_oauthlib.client import OAuth
import os
from realize import settings
from core.oauth.base import OauthBase

oauth_views = Blueprint('oauth_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))
oauth = OAuth(oauth_views)

oauth_handlers = settings.OAUTH_CONFIG.keys()

handlers = {}
login_urls = {}

for handler in oauth_handlers:
    mod = __import__("core.oauth.{0}".format(handler))
    handler_settings = dict(settings.OAUTH_CONFIG[handler].items() + getattr(settings, "{0}_SECRET".format(handler.upper())).items())
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

            login = getattr(obj, "login")
            auth_handler = authorized_handler(login_required(getattr(obj, "authorized")))
            token = token_getter(getattr(obj, "token"))
            handlers[handler] = handler_obj
            oauth_views.add_url_rule(login_url, login_route_name, view_func=login)
            oauth_views.add_url_rule(authorize_url, auth_route_name, view_func=auth_handler)

@login_required
@oauth_views.route("/oauth")
def oauth_accounts():
    auth = current_user.authorizations
    current_auth = {}
    for a in auth:
        current_auth[a.name] = auth
    all_logins = login_urls

    return render_template("oauth.html", current_auth=current_auth, all_logins=all_logins)
