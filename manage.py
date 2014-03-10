from flask.ext.script import Manager
from app import app, initialize_app
from core.commands.database import UpgradeDB
from core.commands.server import RunServer

initialize_app(app)
manager = Manager(app)
manager.add_command('syncdb', UpgradeDB())
manager.add_command('runserver', RunServer())

if __name__ == "__main__":
    manager.run()