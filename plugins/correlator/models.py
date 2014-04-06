from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField, DictField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class Correlations(PluginDataModel):
    metric_proxy = MetricProxy(name="correlations")
    source_proxy = SourceProxy(name="dashingly")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    series1 = Field()
    series2 = Field()
    message = Field()

class DirectionChanges(PluginDataModel):
    metric_proxy = MetricProxy(name="directions")
    source_proxy = SourceProxy(name="dashingly")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    series1 = Field()
    message = Field()
