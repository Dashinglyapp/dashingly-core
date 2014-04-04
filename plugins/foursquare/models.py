from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField, DictField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class Checkins(PluginDataModel):
    metric_proxy = MetricProxy(name="checkins")
    source_proxy = SourceProxy(name="foursquare")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    type = Field()
    source = Field()
    venue = Field()
    location = DictField()
    latitude = Field()
    longitude = Field()
    visit_count = FloatField()
    date = DateTimeField
