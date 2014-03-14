import importlib
import os
import sys
from core.database.manager import DatabaseManager
from app import db
from core.plugins.lib.base import BasePlugin
from core.manager import ExecutionContext
from core.views.manager import ViewManager


class PluginLoader():
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        for (dirpath, dirs, files) in os.walk(self.path):
            if not dirpath in sys.path:
                sys.path.insert(0, dirpath)
            for f in files:
                (name, ext) = os.path.splitext(f)
                if ext == os.extsep + "py" and name == os.path.split(dirpath)[-1]:
                    importlib.import_module(name)
        for plugin in BasePlugin.__subclasses__():
            yield plugin

def load_plugins():
    plugins = {}
    from flask import current_app
    context = ExecutionContext()
    manager = DatabaseManager(context, session=db.session)
    view_manager = ViewManager(context, manager=manager)
    for plugin in PluginLoader(current_app.config['PLUGIN_PATH']):
        # Store plugins in a dictionary for later access.
        plugins[plugin.hashkey] = plugin
        # Register all plugins and create a DB entry as needed.
        manager.register_plugin(plugin)
        view_manager.register_views(plugin)
    db.session.commit()
    return plugins

plugins = load_plugins()