from core.manager import BaseManager, ExecutionContext
from core.plugins.manager import PluginManager
from core.oauth.manager import AuthorizationManager


class InvalidTask(Exception):
    pass

class TaskManager(BaseManager):

    def lookup_plugin(self, plugin_key):
        manager = PluginManager(self.context)
        return manager.lookup_plugin(plugin_key)

    def setup_task(self, task_cls):
        manager = self.get_manager_for_context()
        plugin = self.lookup_plugin(self.plugin.hashkey)
        context = ExecutionContext(user=self.user, plugin=plugin, group=self.group)
        auth_manager = AuthorizationManager(context)

        return task_cls(context=context, manager=manager, auth_manager=auth_manager)

    def run_actions(self, task_cls, action_name, **kwargs):
        task_obj = self.setup_task(task_cls)
        func = getattr(task_obj, action_name)
        return func(**kwargs)

    def run(self, task_cls, **kwargs):
        return self.run_actions(task_cls, "run", **kwargs)