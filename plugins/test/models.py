from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.fields import Field, ListField, DateTimeField, IntegerField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class MoodModel(PluginDataModel):
    metric_proxy = MetricProxy(name="mood")
    source_proxy = SourceProxy(name="self")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))]

    score = IntegerField()

class DataModel(PluginDataModel):
    metric_proxy = MetricProxy(name="data")
    source_proxy = SourceProxy(name="self")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))]

    number = Field()
    text = Field()

class SettingsModel(PluginDataModel):
    metric_proxy = MetricProxy(name="settings")
    source_proxy = SourceProxy(name="self")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))]

    name = Field()
