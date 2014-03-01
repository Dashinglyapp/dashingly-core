from core.manager import BaseManager
from core.plugins.permissions import AuthorizationPermission
from requests_oauthlib import OAuth2Session
from realize import settings

class AuthorizationDoesNotExist(Exception):
    pass

class AuthorizationManager(BaseManager):
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
                client_data = getattr(settings, "{0}_SECRET".format(name.upper()))
                session = OAuth2Session(client_data['consumer_key'], token=authorization.access_token)
                session._client.access_token = authorization.access_token
                return session
        return None
