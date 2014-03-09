from flask import session, request, url_for, jsonify, redirect
from core.oauth.base import OauthV1Base

class FitbitOauth(OauthV1Base):
    handler = "fitbit"
    session_token_name = "fitbit_token"