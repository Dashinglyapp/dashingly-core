from core.plugins.lib.fields import IntegerField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm
from core.tests.base import RealizeTest
from core.tests.util import get_manager
from core.tests.factories import UserFactory, PluginFactory, TimePointFactory, BlobFactory, MetricFactory, SourceFactory, PluginModelFactory
from core.plugins.lib.models import TimePointBase, BlobBase
from core.plugins.lib.proxies import MetricProxy, SourceProxy, PluginProxy, PluginModelProxy
from realize.log import logging
from core.tests.base import db
from mock import patch
from core.plugins.lib.base import BasePlugin

log = logging.getLogger(__name__)

class TestTimeModel(TimePointBase):
    metric_proxy = MetricProxy(name="test")
    source_proxy = SourceProxy(name="test")

class TestBlobModel(BlobBase):
    metric_proxy = MetricProxy(name="test1")
    source_proxy = SourceProxy(name='test1')

    number = IntegerField()

class TestLoosePermissions(TimePointBase):
    metric_proxy = MetricProxy(name="test2")
    source_proxy = SourceProxy(name="test2")
    perms = [Scope(ZonePerm("user", all=True), BlockPerm("plugin", all=True))]

class TestPlugin(BasePlugin):
    name = "test"
    hashkey = "1"
    models = [TestTimeModel, TestBlobModel, TestLoosePermissions]

class DatabaseTest(RealizeTest):
    plugin_classes = [TestPlugin]

    def run_query_assert(self, obj, plugin, times_len, user=None):
        manager = get_manager(plugin, db.session, user=user)
        times = manager.query_time_filter(obj.plugin_proxy, obj.metric_proxy)
        self.assertEqual(len(times), times_len)

    def test_manager(self):
        manager = get_manager(self.plugin_info['1']['plugin'], db.session, user=self.plugin_info['1']['user'])
        bad_user = UserFactory()
        bad_plugin = PluginFactory()

        t_obj = TestTimeModel()
        manager.add(t_obj)

        # We are the wrong user and plugin, so we don't have permissions for this yet.
        self.run_query_assert(t_obj, bad_plugin, 0, bad_user)

        # Right user, wrong plugin.  Should give us nothing.
        self.run_query_assert(t_obj, self.plugin_info['1']['plugin'], 0, bad_user)

        # Wrong user, right plugin.  Should give us nothing.
        self.run_query_assert(t_obj, bad_plugin, 0, self.plugin_info['1']['user'])

        # We are now the correct user and plugin, so we should have permission.
        self.run_query_assert(t_obj, self.plugin_info['1']['plugin'], 1, self.plugin_info['1']['user'])

    def test_wrong_permissions(self):
        manager = get_manager(self.plugin_info['1']['plugin'], db.session, user=self.plugin_info['1']['user'])
        bad_plugin = PluginFactory()

        obj = TestLoosePermissions()
        manager.add(obj)

        # This is 1 because of the object we made, and another because the setUp function makes an instance, which is 2.
        self.run_query_assert(obj, bad_plugin, 2)

    def test_query(self):
        manager = get_manager(self.plugin_info['1']['plugin'], db.session, user=self.plugin_info['1']['user'])
        obj = TestBlobModel()
        manager.add(obj)

        # We have created the object, so querying for it should give us the first instance.
        data = manager.query_blob_first(obj.plugin_proxy, obj.metric_proxy)
        self.assertTrue(isinstance(data, TestBlobModel))