from flask import session, request, url_for, jsonify, redirect
from core.oauth.base import OauthV2Base

class FacebookOauth(OauthV2Base):
    handler = "facebook"
    session_token_name = "facebook_token"