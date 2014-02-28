class BaseView(object):
    name = None
    manager = None
    path = None

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get(self, data):
        raise NotImplementedError()

    def post(self, data):
        raise NotImplementedError()

    def delete(self, data):
        raise NotImplementedError

    def put(self, data):
        raise NotImplementedError()

    def patch(self, data):
        raise NotImplementedError()