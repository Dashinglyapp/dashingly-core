from core.plugins.base import BasePlugin
from core.plugins.proxies import PluginProxy, MetricProxy
from models import MoodModel

class TestPlugin(BasePlugin):
    name = "test"
    description = "The best plugin ever, naturally."
    models = [MoodModel]
    hashkey = "1"

    def setup(self):
        moods = self.wrapper.query_filter(PluginProxy(name=self.name, hashkey=self.hashkey), MetricProxy(name="mood"))
        if len(moods) == 0:
            mood = MoodModel(data=1)
            self.wrapper.add(mood)

    def destroy(self):
        pass