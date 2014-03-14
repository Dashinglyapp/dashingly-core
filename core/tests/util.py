from core.manager import ExecutionContext
from core.tests.factories import UserFactory, PluginFactory

def get_manager(plugin, session, user=None, group=None):
    from core.database.manager import DatabaseManager

    context = ExecutionContext(user=user, plugin=plugin, group=group)
    manager = DatabaseManager(context, session=session)
    return manager