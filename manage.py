from flask.ext.script import Manager
from core.commands.manager import CommandManager
from app import app, initialize_app
from core.commands.database import UpgradeDB, MakeAdmin
from core.commands.server import RunServer
from core.commands.frontend import SyncJS
from core.commands.test import Test
from core.manager import ExecutionContext

initialize_app(app)
manager = Manager(app)
manager.add_command('syncdb', UpgradeDB())
manager.add_command('runserver', RunServer())
manager.add_command('syncjs', SyncJS)
manager.add_command('test', Test)
manager.add_command('makeadmin', MakeAdmin)

context = ExecutionContext()
command_manager = CommandManager(context)
plugin_command_manager = command_manager.get_plugin_command_manager()

manager.add_command('plugins', plugin_command_manager)

if __name__ == "__main__":
    manager.run()