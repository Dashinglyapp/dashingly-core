from flask.ext.script import Manager
from core.commands.manager import CommandManager
from app import app, initialize_app
from core.manager import ExecutionContext

initialize_app(app)
manager = None

def add_commands():
    context = ExecutionContext()
    command_manager = CommandManager(context)
    return command_manager.get_plugin_command_manager(app)

if __name__ == "__main__":
    with app.test_request_context():
        manager = add_commands()
        manager.run()