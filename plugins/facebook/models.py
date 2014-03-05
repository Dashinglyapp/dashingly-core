from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField, IntegerField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class NewsFeed(PluginDataModel):
    metric_proxy = MetricProxy(name="newsfeed")
    source_proxy = MetricProxy(name="facebook")
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

    date = DateTimeField()
    update_time = DateTimeField()
    from_id = Field()
    from_name = Field()
    story = Field()
    type = Field()
    likes = ListField()
    comments = ListField()
    message = Field()
    name = Field()
    shares = IntegerField()
    picture = Field()
