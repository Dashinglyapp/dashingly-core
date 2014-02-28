from core.plugins.proxies import MetricProxy, SourceProxy
from core.plugins.models import TimePointBase, BlobBase
from core.plugins.fields import Field, ListField, DateTimeField, FloatField
from core.plugins.scope import Scope, ZonePerm, BlockPerm

class DailyCommits(TimePointBase):
    metric_proxy = MetricProxy(name="dailycommits")
    source_proxy = SourceProxy(name="github")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    data = FloatField()

class GithubCommits(BlobBase):
    metric_proxy = MetricProxy(name="commits")
    source_proxy = MetricProxy(name="github")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    date = DateTimeField()
    repo_name = Field()
    repo_url = Field()
    message = Field()
    url = Field()
