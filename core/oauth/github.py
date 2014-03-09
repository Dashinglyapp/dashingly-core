from flask import session, request, url_for, redirect
from core.oauth.base import OauthV2Base
from flask.ext.security import login_required

class GithubOauth(OauthV2Base):
    handler = "github"
    session_token_name = "github_token"