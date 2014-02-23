from core.plugins.proxies import MetricProxy, SourceProxy
from core.plugins.models import TimeSeriesBase

class MoodModel(TimeSeriesBase):
    metric_proxy = MetricProxy(name="mood")
    source_proxy = SourceProxy(name="self")

