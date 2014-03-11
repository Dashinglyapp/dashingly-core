from flask.ext.script import Manager
from app import app, initialize_app
from core.commands.database import UpgradeDB, MakeAdmin
from core.commands.server import RunServer
from core.commands.frontend import SyncJS
from core.commands.test import Test

initialize_app(app)
manager = Manager(app)
manager.add_command('syncdb', UpgradeDB())
manager.add_command('runserver', RunServer())
manager.add_command('syncjs', SyncJS)
manager.add_command('test', Test)
manager.add_command('makeadmin', MakeAdmin)

if __name__ == "__main__":
    manager.run()