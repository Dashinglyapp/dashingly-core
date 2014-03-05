from flask.ext.testing import TestCase
from mock import patch
from app import create_test_app, db
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.proxies import SourceProxy, MetricProxy, PluginProxy, PluginModelProxy
from core.tests.factories import PluginDataFactory, MetricFactory, SourceFactory, PluginModelFactory, PluginFactory, UserFactory
from realize.log import logging

app = create_test_app()
db.app = app
db.init_app(app)

log = logging.getLogger(__name__)

class RealizeTest(TestCase):

    def create_app(self):
        return app

    @property
    def plugins(self):
        plugins = {}
        for p in self.plugin_classes:
            plugins[p.hashkey] = p
        return plugins

    def create_bundle(self, metric_name, source_name, plugin, cls):
        if issubclass(cls, PluginDataModel):
            factory = PluginDataFactory
        else:
            raise Exception("Invalid class type for factory.")

        metric = MetricFactory(name=metric_name)
        source = SourceFactory(name=source_name)
        model = PluginModelFactory()
        cls_args = dict(
            metric=metric,
            source=source,
            plugin=plugin,
            plugin_model=model
        )
        inst = factory(**cls_args)
        cls_args.update({
            'source_proxy': SourceProxy(name=source.name),
            'metric_proxy': MetricProxy(name=metric.name),
            'plugin_proxy': PluginProxy(name=plugin.name, hashkey=plugin.hashkey),
            'plugin_model_proxy': PluginModelProxy(metric_id=metric.name, plugin_id=plugin.hashkey, hashkey=model.hashkey, name=model.__class__.__name__),
            'inst': inst
        })
        return cls_args

    def setUp(self):
        db.create_all(app=app)
        self.plugin_info = {}
        for p in self.plugin_classes:
            plugin = PluginFactory(name=p.name, hashkey=p.hashkey)
            user = UserFactory(plugins=[plugin])
            models = {}
            for k in p.models:
                bundle = self.create_bundle(k.metric_proxy.name, k.source_proxy.name, plugin, k)
                k.plugin_proxy = bundle['plugin_proxy']
                k.plugin_model_proxy = bundle['plugin_model_proxy']
                models[k.metric_proxy.name] = k
            self.plugin_info[plugin.hashkey] = {
                'user': user,
                'plugin': plugin,
                'models': models
            }

        self.patcher = patch.dict('core.plugins.loader.plugins', self.plugins)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        db.session.remove()
        db.drop_all()
