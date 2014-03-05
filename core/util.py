from flask.ext.login import current_user
from flask.ext.security import auth_required
from sqlalchemy.exc import IntegrityError


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