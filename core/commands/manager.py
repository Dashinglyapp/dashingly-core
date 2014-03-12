from core.manager import BaseManager
from flask.ext.script import Manager

class CommandManager(BaseManager):
    def get_plugin_command_manager(self):
        from core.plugins.loader import plugins

        plugin_command_manager = Manager()
        for p in plugins:
            sub_manager = Manager()
            plugin = plugins[p]
            db_manager = self.get_manager_from_plugin(plugin)
            for c in plugin.commands:
                c.manager = db_manager
                try:
                    sub_manager.add_command(c.name, c)
                except AttributeError:
                    continue
            plugin_command_manager.add_command(plugin.name, sub_manager)
        return plugin_command_manager
