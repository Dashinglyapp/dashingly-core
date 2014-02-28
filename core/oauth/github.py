from flask import session, request, url_for, jsonify, redirect
from core.oauth.base import OauthBase
from flask.ext.security import login_required

class GithubOauth(OauthBase):
    handler = "github"

    @login_required
    def login(self):
        return self.handler_obj.authorize(callback=url_for('oauth_views.{0}_authorized'.format(self.handler), _external=True))

    @login_required
    def authorized(self, resp):
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['github_token'] = (resp['access_token'], '')
        auth = self.get_or_create(self.handler, access_token=resp['access_token'])
        return redirect(url_for('oauth_views.oauth_accounts'))

    def token(self):
        return session.get('github_token')