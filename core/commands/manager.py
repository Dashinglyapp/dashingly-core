from core.manager import BaseManager
from flask.ext.script import Manager
from flask import Flask

class CustomCommandManager(Manager):
     def create_app(self, **kwargs):
        if self.parent:
            # Sub-manager, defer to parent Manager
            return self.parent.create_app(**kwargs)

        if isinstance(self.app, Flask):
            if "settings" in kwargs:
                self.app.config.from_object(kwargs['settings'])
            return self.app

        return self.app(**kwargs)

class CommandManager(BaseManager):
    def get_plugin_command_manager(self, app):
        from core.plugins.loader import plugins

        plugin_command_manager = Manager(app)
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
