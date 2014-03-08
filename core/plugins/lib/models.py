from core.database.models import PluginData
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm
from fields import Field, FloatField, DictField, DateTimeField, IntegerField
import json
from realize.log import logging

log = logging.getLogger(__name__)

class DuplicateRecord(Exception):
    pass

class ModelBase(object):
    reserved_keys = ["id", "hashkey", "date", "created", "modified"]
    id = IntegerField()
    hashkey = Field()
    date = DateTimeField()
    created = DateTimeField()
    modified = DateTimeField()

    metric_proxy = None
    source_proxy = None
    model_cls = None
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))]

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get_data(self):
        raise NotImplementedError()

    def set_data(self, data):
        raise NotImplementedError()

    @property
    def fields(self):
        fields_list = []
        for p in dir(self):
            prop = getattr(self, p)
            if isinstance(prop, Field):
                fields_list.append(prop)
        return fields_list

class PluginDataModel(ModelBase):
    model_cls = PluginData

    def get_fields(self):
        cls = self.__class__
        fields = []
        for f in dir(cls):
            if isinstance(getattr(cls, f), Field) and f not in self.reserved_keys:
                fields.append(f)
        return fields

    def get_to_json(self, f):
        cls = self.__class__
        field_cls = getattr(cls, f).__class__
        return field_cls.to_json

    def get_data(self):
        data = {}
        for f in self.get_fields():
            data[f] = self.get_to_json(f)(getattr(self, f))
        return json.dumps(data)

    def set_data(self, data):
        try:
            data = json.loads(data)
        except Exception:
            log.error("Could not load data.")
            data = {}

        for f in self.get_fields():
            if f in data:
                setattr(self, f, data[f])