from flask import session, request, url_for, redirect
from core.oauth.base import OauthV2Base
from flask.ext.security import login_required

class FoursquareOauth(OauthV2Base):
    handler = "foursquare"
    session_token_name = "foursquare_token"