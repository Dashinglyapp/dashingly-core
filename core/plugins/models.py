from core.database.models import TimePoint
from fields import Field, FloatField

class ModelContext(object):
    """
    Should specify user and plugin generally.
    """
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

class ModelBase(object):
    id = Field()
    hashkey = Field()
    date = Field()
    created = Field()
    modified = Field()

    metric_proxy = None
    source_proxy = None
    model_cls = None

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

class TimeSeriesBase(ModelBase):
    model_cls = TimePoint
    data = FloatField()