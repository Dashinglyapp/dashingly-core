from flask import session, request, url_for, jsonify, redirect
from core.oauth.base import OauthBase

class FacebookOauth(OauthBase):
    handler = "facebook"
    session_token_name = "facebook_token"