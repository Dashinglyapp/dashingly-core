from core.plugins.proxies import MetricProxy, SourceProxy
from core.plugins.models import TimePointBase, BlobBase
from core.plugins.fields import Field, ListField, DateTimeField
from core.plugins.scope import Scope, ZonePerm, BlockPerm

class MoodModel(TimePointBase):
    metric_proxy = MetricProxy(name="mood")
    source_proxy = SourceProxy(name="self")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))]

class DataModel(BlobBase):
    metric_proxy = MetricProxy(name="data")
    source_proxy = SourceProxy(name="self")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))]

    number = Field()
    text = Field()
