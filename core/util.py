from flask.ext.login import current_user
from flask.ext.security import auth_required
from flask import url_for, request, current_app
from flask.ext.security.utils import md5
from sqlalchemy.exc import IntegrityError
from core.database.models import Group, User
from core.manager import ExecutionContext

def api_url_for(namespace, cls, **values):
    return url_for("{0}.{1}".format(namespace, cls.endpoint), **values)

class NotOwnerException(Exception):
    pass

class InvalidScopeException(Exception):
    pass

class InvalidObjectException(Exception):
    pass

class IncorrectPermissionsException(Exception):
    pass

DEFAULT_SECURITY = auth_required('token', 'session')

def get_cls(session, cls, obj, attrs=None, create=False):
    if attrs is None:
        attrs = ["name"]
    query = session.query(cls)
    for attr in attrs:
        query = query.filter(getattr(cls, attr) == getattr(obj, attr))
    count = query.count()
    if count > 0:
        val = query.first()
    elif create:
        val = cls()
        for attr in attrs:
            setattr(val, attr, getattr(obj, attr))
        session.add(val)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
    else:
        raise InvalidObjectException()

    return val

def append_container(data, name=None, tags=None, code=200, data_key='modules'):
    return {
        'name': name,
        'tags': tags,
        data_key: data,
        'meta': {'code': code}
    }

def lookup_group(hashkey):
    return Group.query.filter(Group.hashkey == hashkey).first()

def lookup_user(hashkey):
    return User.query.filter_by(hashkey=hashkey).first()

def check_ownership(group):
    return current_user == group.owner

def lookup_and_check(hashkey):
    group = lookup_group(hashkey)
    ownership = check_ownership(group)
    if ownership is False:
        raise NotOwnerException()
    return group

def get_context_for_scope(scope, hashkey):
    context = ExecutionContext()
    if scope == "user":
        mod = lookup_user(hashkey)
        context.user = mod
    elif scope == "group":
        mod = lookup_group(hashkey)
        context.group = mod
    else:
        raise InvalidScopeException()
    return context, mod

def get_data():
    return request.get_json(force=True, silent=True)

def check_token(token):
    try:
        data = current_app.extensions['security'].remember_token_serializer.loads(token, max_age=current_app.config['MAX_TOKEN_AGE'])
        user = current_app.extensions['security'].datastore.find_user(id=data[0])
        if user and md5(user.password) == data[1]:
            return user
    except Exception:
        pass
    return None