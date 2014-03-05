from flask import session, request, url_for, redirect
from core.oauth.base import OauthBase
from flask.ext.security import login_required

class GithubOauth(OauthBase):
    handler = "github"
    session_token_name = "github_token"