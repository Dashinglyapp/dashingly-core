from dateutil import parser
from weakref import WeakKeyDictionary

class DataTypes(object):
    date = "date"
    integer = "integer"
    float = "float"
    string = "string"
    list = "list"
    dictionary = "dictionary"
    none = "none"

class Field(object):
    """
    Basic field class.  Used to store values.
    """
    datatype = DataTypes.string
    def __init__(self, default=None, label=None, help_text=None, scope=None):
        if getattr(self, 'value', None) is None:
            self.value = default
        self.label = label
        self.help_text = help_text
        self.scope = scope
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, obj, obj_type):
        if obj is None:
            return self
        return self.from_json(self.data.get(obj, self.default))

    def __set__(self, obj, value):
        self.data[obj] = self.to_json(value)

    @classmethod
    def from_json(cls, value):
        return value

    @classmethod
    def to_json(cls, value):
        return value

class FloatField(Field):
    datatype = DataTypes.float
    @classmethod
    def from_json(cls, value):
        try:
            return float(value)
        except:
            return 0

class IntegerField(Field):
    datatype = DataTypes.integer
    @classmethod
    def from_json(cls, value):
        try:
            return int(value)
        except:
            return 0

class DateTimeField(Field):
    datatype = DataTypes.integer
    @classmethod
    def from_json(cls, value):
        if isinstance(value, basestring):
            return parser.parse(value)
        return value

    @classmethod
    def to_json(cls, value):
        if isinstance(value, basestring):
            return value
        if value is not None:
            return value.isoformat()
        return None

class ListField(Field):
    """
    A field that stores lists.
    """
    datatype = DataTypes.list
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
    datatype = DataTypes.dictionary
    def __init__(self, **kwargs):
        super(DictField, self).__init__(**kwargs)
        if self.default is None:
            self.default = {}
        if self.value is None:
            self.value = self.default
