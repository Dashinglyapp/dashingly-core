from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import BlobBase
from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class DailyCommits(BlobBase):
    metric_proxy = MetricProxy(name="dailycommits")
    source_proxy = SourceProxy(name="github")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    count = FloatField()

class GithubCommits(BlobBase):
    metric_proxy = MetricProxy(name="commits")
    source_proxy = MetricProxy(name="github")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    date = DateTimeField()
    repo_name = Field()
    repo_url = Field()
    message = Field()
    url = Field()
