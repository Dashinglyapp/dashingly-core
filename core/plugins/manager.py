from flask.ext.login import current_user
from core.plugins.views import ViewManager
from core.util import get_cls
from core.manager import BaseManager, ExecutionContext
from flask import jsonify

class InvalidMethodException(Exception):
    pass

class InvalidRouteException(Exception):
    pass

class PluginManager(BaseManager):
    def list(self):
        return self.user.plugins

    def call_view_handler(self, path, method, data):
        context = ExecutionContext(plugin=self.plugin, user=current_user)
        view_manager = ViewManager(context)
        return view_manager.handle_route(path, method, data)

    def call_form_handler(self, path, method, data):
        plugin_cls = self.get_plugin(self.plugin.hashkey)
        for form_cls in plugin_cls.forms:
            if form_cls.name == path:
                manager = self.get_manager_from_hashkey(self.plugin.hashkey)
                form = form_cls(**data)
                form.context = self.context
                form.manager = manager
                func = getattr(form, method)
                return jsonify(func())

        raise InvalidRouteException()

    def call_route_handler(self, path, method, data):
        if path.startswith("views/"):
            path = path[6:]
            return self.call_view_handler(path, method, data)

        raise InvalidRouteException()

    def run_actions(self, plugin_hashkey, action_name, **kwargs):
        plugin_cls = self.get_plugin(plugin_hashkey)
        manager = self.get_manager_from_hashkey(plugin_hashkey)
        context = ExecutionContext(plugin=self.lookup_plugin(plugin_hashkey), user=self.user)
        plugin = plugin_cls(context, manager)
        func = getattr(plugin, action_name)
        return func(**kwargs)

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

    def get_settings(self, plugin_hashkey, data):
        plugin_cls = self.get_plugin(plugin_hashkey)
        manager = self.get_manager_from_hashkey(plugin_hashkey)
        if plugin_cls.settings_form is None:
            return jsonify({})

        obj_cls = plugin_cls.settings_form.model
        obj = obj_cls()
        obj = manager.get_or_create(obj, query_data=False)
        form = plugin_cls.settings_form()
        for f in form:
            setattr(form, f.name, getattr(obj, f.name, None))

        return jsonify(form.as_json())
