from core.manager import BaseManager

class TaskManager(BaseManager):

    def run_actions(self, task_cls, action_name, **kwargs):
        manager = self.get_manager()
        func = getattr(task_cls, action_name)
        return func(**kwargs)

    def get_manager(self):
        from core.plugins.manager import PluginManager
        manager = PluginManager(self.context)
        manager = manager.get_manager(self.plugin.hashkey)
        return manager

    def run(self, task_cls):
        return self.run_actions(task_cls, "run")