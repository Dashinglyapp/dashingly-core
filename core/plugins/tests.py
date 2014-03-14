import hashlib
from wtforms import TextField
from core.manager import ExecutionContext
from core.plugins.lib.fields import IntegerField, Field
from core.plugins.lib.views.forms import SettingsFormView
from core.tests.base import RealizeTest
from core.tests.factories import UserFactory
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.base import BasePlugin
from manager import PluginManager
from lib.views.base import View
from lib.views.charts import ModelChartView
from realize.log import logging
from flask import current_app
from flask.ext.login import login_user, logout_user

log = logging.getLogger(__name__)

class TestModel(PluginDataModel):
    metric_proxy = MetricProxy(name="test1")
    source_proxy = SourceProxy(name='test1')

    number = IntegerField()

class SettingsModel(PluginDataModel):
    metric_proxy = MetricProxy(name="settings")
    source_proxy = SourceProxy(name="self")
    name = Field()

class TestSettingsForm(SettingsFormView):
    model = SettingsModel
    setting_name = TextField(description="Your name or something like it.")

class TestModelView(ModelChartView):
    name = 'test_chart'
    description = 'A super awesome test chart.'
    model = TestModel
    y_data_field = 'number'
    x_data_field = 'date'

class TestView(View):
    name = "test"
    children = [TestModelView, TestSettingsForm]

class TestPlugin(BasePlugin):
    name = "test"
    hashkey = "1"
    models = [TestModel, SettingsModel]
    views = [TestView]
    settings_form = TestSettingsForm

class PluginManagerTest(RealizeTest):
    plugin_classes = [TestPlugin]

    def test_add_remove(self):
        user = UserFactory()
        context = ExecutionContext(user=user, plugin=self.plugin_info['1']['plugin'])
        manager = PluginManager(context)

        # This should be 1 because we have just added a plugin for the user.
        plugin_key = self.plugin_info['1']['plugin'].hashkey
        manager.add(plugin_key)
        self.assertEqual(len(user.plugins), 1)

        manager.remove(plugin_key)
        self.assertEqual(len(user.plugins), 0)

    def test_get_route(self):
        context = ExecutionContext(user=self.plugin_info['1']['user'], plugin=self.plugin_info['1']['plugin'])
        login_user(self.plugin_info['1']['user'])
        manager = PluginManager(context)
        response = manager.call_route_handler(self.plugin_info['1']['views']['test'].hashkey, "get", {}, None)
        logout_user()

        self.assertEqual(response.status_code, 200)

    def test_get_settings(self):
        context = ExecutionContext(user=self.plugin_info['1']['user'], plugin=self.plugin_info['1']['plugin'])
        manager = PluginManager(context)

        # Should return the response from the view.
        response = manager.get_settings(self.plugin_info['1']['plugin'].hashkey)
        self.assertTrue(isinstance(response, dict))


