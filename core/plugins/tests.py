from wtforms import TextField
from core.manager import ExecutionContext
from core.plugins.lib.fields import IntegerField, Field
from core.plugins.lib.forms import SettingsForm
from core.tests.base import RealizeTest
from core.tests.factories import UserFactory
from core.plugins.lib.models import BlobBase
from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.base import BasePlugin
from manager import PluginManager
from lib.views import WidgetView, ModelChartWidget
from realize.log import logging

log = logging.getLogger(__name__)

class TestBlobModel(BlobBase):
    metric_proxy = MetricProxy(name="test1")
    source_proxy = SourceProxy(name='test1')

    number = IntegerField()

class SettingsModel(BlobBase):
    metric_proxy = MetricProxy(name="settings")
    source_proxy = SourceProxy(name="self")
    name = Field()

class TestSettingsForm(SettingsForm):
    model = SettingsModel
    name = TextField(description="Your name or something like it.")

class TestWidgetView(WidgetView):
    path = "test"
    widgets = {
        'chart': ModelChartWidget(
            'test_chart',
            'A super awesome test chart.',
            model=TestBlobModel,
            y_data_field='number',
            x_data_field='date'
        )
    }

class TestPlugin(BasePlugin):
    name = "test"
    hashkey = "1"
    models = [TestBlobModel, SettingsModel]
    views = [TestWidgetView]
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
        manager = PluginManager(context)
        response = manager.call_route_handler("test/chart", "get", {})

        self.assertTrue(isinstance(response, dict))

    def test_get_settings(self):
        context = ExecutionContext(user=self.plugin_info['1']['user'], plugin=self.plugin_info['1']['plugin'])
        manager = PluginManager(context)

        # Should return the response from the widget.
        response = manager.get_settings(self.plugin_info['1']['plugin'].hashkey, {})
        self.assertEqual(response.status_code, 200)


