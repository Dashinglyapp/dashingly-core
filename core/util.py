class InvalidObjectException(Exception):
    pass

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
    else:
        raise InvalidObjectException()

    return val