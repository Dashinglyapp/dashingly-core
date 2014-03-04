from flask.ext.login import current_user
from flask.ext.security import auth_required

class InvalidObjectException(Exception):
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
        session.commit()
    else:
        raise InvalidObjectException()

    return val

def append_container(data, name=None, tags=None, code=200):
    return {
        'name': name,
        'tags': tags,
        'modules': data,
        'meta': {'code': code}
    }