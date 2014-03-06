from flask.ext.login import current_user
from core.plugins.views import ViewManager
from core.util import get_cls
from core.manager import BaseManager, ExecutionContext
from flask import jsonify

class InvalidMethodException(Exception):
    pass

class InvalidRouteException(Exception):
    pass

class PluginActionRunner(object):
    def __init__(self, context):
        self.context = context
        self.manager = PluginManager(context)

    def add(self, plugin_hashkey):
        return self.manager.add(plugin_hashkey)

    def remove(self, plugin_hashkey):
        return self.manager.remove(plugin_hashkey)

    def configure(self, plugin_hashkey, data):
        return self.manager.get_settings(plugin_hashkey, data)

class PluginManager(BaseManager):
    def list(self):
        return self.user.plugins

    def call_view_handler(self, view_hashkey, method, data):
        context = ExecutionContext(plugin=self.plugin, user=current_user)
        view_manager = ViewManager(context)
        return view_manager.handle_route(view_hashkey, method, data)

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

    def call_route_handler(self, view_hashkey, method, data):
        return self.call_view_handler(view_hashkey, method, data)

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
        if plugin_cls.setup_task is not None:
            self.run_task(plugin_hashkey, plugin_cls.setup_task)
        db.session.commit()

    def run_task(self, plugin_hashkey, task_cls):
        from core.plugins.lib.proxies import TaskProxy
        from core.tasks.runner import run_delayed_task

        run_delayed_task.delay(
            plugin_hashkey,
            TaskProxy(name=task_cls.name),
            user_id=self.user.id,
            group_id=None
        )

    def remove(self, plugin_hashkey):
        from app import db
        from core.plugins.loader import plugins

        plugin_cls = plugins[plugin_hashkey]
        plugin = self.lookup_plugin(plugin_hashkey)
        if plugin in self.user.plugins:
            self.user.plugins.remove(plugin)

        if plugin_cls.remove_task is not None:
            self.run_task(plugin_hashkey, plugin_cls.remove_task)
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
