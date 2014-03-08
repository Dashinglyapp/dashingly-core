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