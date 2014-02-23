class Field(object):
    """
    Basic field class.  Used to store values.
    """
    def __init__(self, default=None, label=None, help_text=None, scope=None):
        if getattr(self, 'value', None) is None:
            self.value = default
        self.label = label
        self.help_text = help_text
        self.scope = scope
        self.default = default

    def __get__(self, obj, obj_type):
        if obj is None:
            return self
        return self.from_json(self.value)

    def __set__(self, obj, value):
        self.value = self.to_json(value)

    @classmethod
    def from_json(cls, value):
        return value

    @classmethod
    def to_json(cls, value):
        return value

class FloatField(Field):
    @classmethod
    def from_json(cls, value):
        return float(value)

class ListField(Field):
    """
    A field that stores lists.
    """
    def __init__(self, **kwargs):
        super(ListField, self).__init__(**kwargs)
        if self.default is None:
            self.default = []
        if self.value is None:
            self.value = self.default

    def append(self, item):
        self.value.append(item)

    def __iter__(self):
        for val in self.value:
            yield val

    def __getitem__(self, k):
        return self.value[k]

    def __len__(self):
        return len(self.value)

class DictField(Field):
    """
    A field that stores dictionaries.
    """
    def __init__(self, **kwargs):
        super(DictField, self).__init__(**kwargs)
        if self.default is None:
            self.default = {}
        if self.value is None:
            self.value = self.default
