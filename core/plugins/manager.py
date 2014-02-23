from core.util import get_cls

class PluginManager(object):
    def __init__(self, user):
        self.user = user

    def list(self):
        return self.user.plugins

    def lookup_plugin(self, plugin_hashkey):
        from core.database.models import Plugin, db
        return db.session.query(Plugin).filter(Plugin.hashkey == plugin_hashkey).first()

    def run_actions(self, plugin_hashkey, action_name):
        from core.plugins.loader import plugins
        from core.database.models import db
        from core.database.wrapper import DBWrapper
        from core.plugins.models import ModelContext
        plugin_cls = plugins[plugin_hashkey]
        plugin_obj = self.lookup_plugin(plugin_hashkey)
        context = ModelContext(user=self.user, plugin=plugin_obj)
        wrapper = DBWrapper(db.session, context)
        plugin = plugin_cls(context, wrapper)
        func = getattr(plugin, action_name)
        func()

    def add(self, plugin_hashkey):
        from core.database.models import db
        from core.plugins.loader import plugins
        from core.database.models import Metric, Source

        plugin_cls = plugins[plugin_hashkey]
        plugin = self.lookup_plugin(plugin_hashkey)
        if plugin not in self.user.plugins:
            self.user.plugins.append(plugin)

        self.run_actions(plugin_hashkey, "setup")
        if plugin_cls.models is not None:
            for m in plugin_cls.models:
                metric = get_cls(db.session, Metric, m.metric_proxy, create=True)
                source = get_cls(db.session, Source, m.source_proxy, create=True)
                if metric not in self.user.metrics:
                    self.user.metrics.append(metric)
                if source not in self.user.sources:
                    self.user.sources.append(source)
        db.session.commit()

    def remove(self, plugin_hashkey):
        from core.database.models import db
        from core.plugins.loader import plugins
        from core.database.models import Metric, Source

        plugin_cls = plugins[plugin_hashkey]
        plugin = self.lookup_plugin(plugin_hashkey)
        if plugin in self.user.plugins:
            self.user.plugins.remove(plugin)

        self.run_actions(plugin_hashkey, "destroy")
        if plugin_cls.models is not None:
            for m in plugin_cls.models:
                metric = get_cls(db.session, Metric, m.metric_proxy, create=True)
                source = get_cls(db.session, Source, m.source_proxy, create=True)
                if metric in self.user.metrics:
                    self.user.metrics.remove(metric)
                if source in self.user.sources:
                    self.user.sources.remove(source)
        db.session.commit()