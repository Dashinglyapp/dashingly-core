from flask.ext.script import Manager
from core.commands.manager import CustomCommandManager
from app import initialize_app, app
from core.manager import ExecutionContext

initialize_app(app)
manager = CustomCommandManager(app)
manager.add_option('-s', '--settings', dest='settings', required=False)

def add_commands(manager):
    from core.commands.database import UpgradeDB, MakeAdmin, GenerateMigration
    from core.commands.server import RunServer
    from core.commands.frontend import SyncJS
    from core.commands.test import Test
    manager.add_command('syncdb', UpgradeDB())
    manager.add_command('schemamigration', GenerateMigration)
    manager.add_command('runserver', RunServer())
    manager.add_command('syncjs', SyncJS)
    manager.add_command('test', Test)
    manager.add_command('makeadmin', MakeAdmin)

if __name__ == "__main__":
    with app.test_request_context():
        add_commands(manager)
        manager.run()