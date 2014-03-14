from flask import session, request, url_for, redirect
from core.oauth.base import OauthV2Base
from flask.ext.security import login_required

class GoogleOauth(OauthV2Base):
    handler = "google"
    session_token_name = "google_token"