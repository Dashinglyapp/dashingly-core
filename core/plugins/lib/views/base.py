class BaseView(object):
    name = None
    manager = None
    path = None
    children = []
    tags = ["view"]

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

class View(BaseView):
    name = None
    description = None
    hashkey = None
    path = None
    children = []
    tags = ["view"]

    def get(self, data):
        data = self.to_json(data)
        meta = self.__class__.meta()
        meta.update({
            'data': data
        })
        return meta

    @classmethod
    def meta(cls):
        return {
            'tree': cls.tree(),
            'name': cls.name,
            'description': cls.description,
            'hashkey': cls.hashkey,
            'url': cls.path,
            'tags': cls.tags
        }

    def post(self, data):
        raise NotImplementedError()

    def save(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def tree(cls):
        children = []
        for c in cls.children:
            children.append(c.meta())
        return children

    def to_json(self, data):
        return {}