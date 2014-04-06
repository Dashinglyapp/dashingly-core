from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField, DictField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class EHRData(PluginDataModel):
    metric_proxy = MetricProxy(name="patientdata")
    source_proxy = SourceProxy(name="ehr")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    data = DictField()
