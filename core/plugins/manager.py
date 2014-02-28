from core.util import get_cls
from core.manager import BaseManager, ExecutionContext

class InvalidMethodException(Exception):
    pass

class InvalidRouteException(Exception):
    pass

class PluginManager(BaseManager):
    def list(self):
        return self.user.plugins

    def get_plugin(self, plugin_hashkey):
        from core.plugins.loader import plugins
        plugin_cls = plugins[plugin_hashkey]
        return plugin_cls

    def call_route_handler(self, path, method, data):
        plugin_cls = self.get_plugin(self.plugin.hashkey)
        for view_cls in plugin_cls.views:
            if view_cls.path == path:
                manager = self.get_manager(self.plugin.hashkey)
                view = view_cls(context=self.context, manager=manager)
                func = getattr(view, method)
                return func(data)
        raise InvalidRouteException()

    def run_actions(self, plugin_hashkey, action_name, **kwargs):
        plugin_cls = self.get_plugin(plugin_hashkey)
        manager = self.get_manager(plugin_hashkey)
        context = ExecutionContext(plugin=self.lookup_plugin(plugin_hashkey), user=self.user)
        plugin = plugin_cls(context, manager)
        func = getattr(plugin, action_name)
        return func(**kwargs)

    def get_manager(self, plugin_hashkey):
        from app import db
        from core.database.manager import DBManager

        plugin = self.lookup_plugin(plugin_hashkey)
        context = ExecutionContext(user=self.user, plugin=plugin, group=self.group)
        manager = DBManager(context, session=db.session)
        return manager

    def add(self, plugin_hashkey):
        from app import db
        from core.plugins.loader import plugins
        from core.database.models import Metric, Source

        plugin_cls = plugins[plugin_hashkey]
        plugin = self.lookup_plugin(plugin_hashkey)
        if plugin not in self.user.plugins:
            self.user.plugins.append(plugin)

        if plugin_cls.models is not None:
            for m in plugin_cls.models:
                metric = get_cls(db.session, Metric, m.metric_proxy, create=True)
                source = get_cls(db.session, Source, m.source_proxy, create=True)
                if metric not in self.user.metrics:
                    self.user.metrics.append(metric)
                if source not in self.user.sources:
                    self.user.sources.append(source)
        self.run_actions(plugin_hashkey, "setup")
        db.session.commit()

    def remove(self, plugin_hashkey):
        from app import db
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

    def save_form(self, plugin_hashkey, metric_name, **kwargs):
        from proxies import MetricProxy
        return self.run_actions(plugin_hashkey, "save_forms", metric=MetricProxy(name=metric_name), **kwargs)