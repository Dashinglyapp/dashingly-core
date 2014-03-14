from flask.ext.testing import TestCase
from mock import patch
from app import create_app, db, initialize_base_app
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.proxies import SourceProxy, MetricProxy, PluginProxy, PluginModelProxy
from core.tests.factories import PluginDataFactory, MetricFactory, SourceFactory, PluginModelFactory, PluginFactory, UserFactory, PluginViewFactory
from realize.log import logging

log = logging.getLogger(__name__)

class RealizeTest(TestCase):
    plugin_classes = []
    def create_app(self):
        app = create_app("realize.test_settings")
        with app.test_request_context():
            initialize_base_app(app)
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

    def create_view(self, view_name, plugin):
        factory = PluginViewFactory
        inst = factory(
            name=view_name,
            plugin=plugin
        )
        return inst

    def setUp(self):
        db.create_all(app=self.app)
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

            views = {}
            for v in p.views:
                view = self.create_view(v.name, plugin)
                views[view.name] = view

            self.plugin_info[plugin.hashkey] = {
                'user': user,
                'plugin': plugin,
                'models': models,
                'views': views
            }

        self.patcher = patch.dict('core.plugins.loader.plugins', self.plugins)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        db.session.remove()
        db.drop_all()
