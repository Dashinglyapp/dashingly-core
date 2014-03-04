from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.test.models import MoodModel, DataModel, SettingsModel
from plugins.test.views import GetStuffView, SettingsForm
from datetime import datetime
from plugins.test import manifest

class TestPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [MoodModel, DataModel, SettingsModel]
    settings_form = SettingsForm
    views = [GetStuffView]
    hashkey = manifest.HASHKEY

    def setup(self):
        moods = self.manager.query_time_filter(manifest.plugin_proxy, MetricProxy(name="mood"))
        if len(moods) == 0:
            mood = MoodModel(data=1, date=datetime.utcnow())
            self.manager.add(mood)
        data = self.manager.query_blob_filter(manifest.plugin_proxy, MetricProxy(name="data"))
        if len(data) == 0:
            data = DataModel(date=datetime.utcnow(), text="This is some text.", number=1)
            self.manager.add(data)

    def destroy(self):
        pass