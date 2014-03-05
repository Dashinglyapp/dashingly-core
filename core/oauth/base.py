from functools import wraps
from flask import url_for, session, request, current_app, _request_ctx_stack
from flask.ext.principal import identity_changed, Identity
from flask.ext.security.decorators import _get_unauthorized_response
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import redirect
from flask.ext.login import current_user
from core.database.models import User
from realize import settings

def get_serializer():
    return URLSafeTimedSerializer(settings.SECRET_KEY)

def state_token_required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if _check_state_token():
            return fn(*args, **kwargs)
        return _get_unauthorized_response()
    return decorated

def _check_state_token():
    serializer = get_serializer()
    state = request.args.get('state', None)
    id = serializer.loads(state)[0]
    user = User.query.filter(User.id == int(id)).first()

    if user and user.is_authenticated():
        app = current_app._get_current_object()
        _request_ctx_stack.top.user = user
        identity_changed.send(app, identity=Identity(user.id))
        return True

    return False

class OauthBase(object):
    handler = None
    access_token_name = "access_token"
    refresh_token_name = "refresh_token"
    session_token_name = "generic_token"

    def __init__(self, handler_obj):
        self.handler_obj = handler_obj

    def generate_oauth_state_token(self):
        serializer = get_serializer()
        return serializer.dumps([current_user.id, current_user.email])

    def login(self):
        return self.handler_obj.authorize(
            callback=url_for(
                'oauth_views.{0}_authorized'.format(self.handler),
                _external=True,
                state=self.generate_oauth_state_token()
            ))

    def authorized(self, resp):
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session[self.session_token_name] = (resp[self.access_token_name], '')
        auth = self.get_or_create(
            self.handler,
            access_token=resp.get(self.access_token_name, None),
            refresh_token=resp.get(self.refresh_token_name, None)
        )
        return redirect(url_for('oauth_views.authorizations'))

    def get_or_create(self, name, **kwargs):
        from core.database.models import Authorization
        from flask.ext.login import current_user
        from app import db

        inst = db.session.query(Authorization).filter_by(name=name, user=current_user).first()
        if inst:
            for k in kwargs:
                setattr(inst, k, kwargs[k])
        else:
            inst = Authorization(name=name, user=current_user, **kwargs)
            db.session.add(inst)
        db.session.commit()

    def token(self):
        return session.get(self.session_token_name)