from core.plugins.proxies import MetricProxy, SourceProxy
from core.plugins.models import TimePointBase, BlobBase
from core.plugins.fields import Field, ListField

class MoodModel(TimePointBase):
    metric_proxy = MetricProxy(name="mood")
    source_proxy = SourceProxy(name="self")

class DataModel(BlobBase):
    metric_proxy = MetricProxy(name="data")
    source_proxy = SourceProxy(name="self")

    number = Field()
    text = Field()

