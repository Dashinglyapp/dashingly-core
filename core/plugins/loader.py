import importlib
import os
import sys
from core.database.manager import DBManager
from app import db
from core.plugins.base import BasePlugin
from core.manager import ExecutionContext

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
    from realize import settings
    context = ExecutionContext()
    manager = DBManager(context, session=db.session)
    for plugin in PluginLoader(settings.PLUGIN_PATH):
        # Store plugins in a dictionary for later access.
        plugins[plugin.hashkey] = plugin
        # Register all plugins and create a DB entry as needed.
        manager.register_plugin(plugin)
    db.session.commit()
    return plugins

plugins = load_plugins()