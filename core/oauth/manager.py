from core.manager import BaseManager
from core.plugins.lib.permissions import AuthorizationPermission
from requests_oauthlib import OAuth2Session, OAuth1Session
from flask import current_app

class AuthorizationDoesNotExist(Exception):
    pass

class InvalidOauthVersion(Exception):
    pass

class AuthorizationManager(BaseManager):
    def get_permissions(self):
        from core.plugins.loader import plugins
        plugin = plugins[self.plugin.hashkey]
        return {
            'authorizations': [p.name for p in plugin.permissions if isinstance(p, AuthorizationPermission)]
        }

    def get_auth(self, name):
        from core.plugins.loader import plugins
        from app import db
        from core.database.models import Authorization

        plugin = plugins[self.plugin.hashkey]

        for p in plugin.permissions:
            if isinstance(p, AuthorizationPermission) and p.name == name:
                authorization = db.session.query(Authorization).filter(
                    Authorization.user == self.user,
                    Authorization.name == name
                )
                if authorization.count() == 0:
                    return None
                else:
                    authorization = authorization[-1]
                client_data = current_app.config.get("{0}_SECRET".format(name.upper()))
                if authorization.version == 1:
                    session = OAuth1Session(
                        client_data['consumer_key'],
                        client_secret=client_data['consumer_secret'],
                        resource_owner_key=authorization.oauth_token,
                        resource_owner_secret=authorization.oauth_token_secret
                    )
                elif authorization.version == 2:
                    session = OAuth2Session(
                        client_data['consumer_key'],
                        token=authorization.access_token
                    )
                    session._client.access_token = authorization.access_token
                else:
                    raise InvalidOauthVersion()

                return session
        return None
