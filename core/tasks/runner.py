from app import celery
from core.database.models import User, Plugin, Group
from core.manager import ExecutionContext
from core.tasks.manager import TaskManager

class InvalidZoneException(Exception):
    pass

class ManagerWrapper(object):
    def __init__(self, plugin_hashkey, user_id=None, group_id=None):
        from core.plugins.loader import plugins
        self.plugin_hashkey = plugin_hashkey
        self.user_id = user_id
        self.group_id = group_id

        self.plugin = plugins[plugin_hashkey]

    def get_manager_user(self):
        user = User.query.filter(User.id == self.user_id).first()
        context = ExecutionContext(user=user, plugin=self.plugin)
        return TaskManager(context)

    def get_manager_group(self):
        group = Group.query.filter(Group.id == self.group_id).first()
        context = ExecutionContext(group=group, plugin=self.plugin)
        return TaskManager(context)


def get_manager(plugin_hashkey, user_id, group_id):
    if user_id is not None:
        wrapper = ManagerWrapper(plugin_hashkey, user_id=user_id)
        manager = wrapper.get_manager_user()
    elif group_id is not None:
        wrapper = ManagerWrapper(plugin_hashkey, group_id=group_id)
        manager = wrapper.get_manager_group()
    else:
        raise InvalidZoneException()
    return manager, wrapper

@celery.task()
def run_delayed_plugin(plugin_hashkey, user_id=None, group_id=None, interval=None):
    manager, wrapper = get_manager(plugin_hashkey, user_id, group_id)

    tasks = wrapper.plugin.tasks
    for task in tasks:
        user_task = user_id is not None and task.scope.zone == "user"
        group_task = group_id is not None and task.scope.zone == "group"
        if task.interval == interval and (user_task or group_task):
            manager.run(task)

@celery.task()
def run_delayed_task(plugin_hashkey, task_proxy, user_id=None, group_id=None):
    manager, wrapper = get_manager(plugin_hashkey, user_id, group_id)

    tasks = wrapper.plugin.tasks
    for task in tasks:
        if task.task_proxy.name == task_proxy.name:
            manager.run(task)

@celery.task()
def run_interval_tasks(interval):
    from core.plugins.loader import plugins
    for user in User.query.all():
        for plugin in user.plugins:
            run_delayed_plugin.delay(plugin.hashkey, user_id=user.id, interval=interval)

    for group in Group.query.all():
        for plugin in plugins:
            run_delayed_plugin.delay(plugin.hashkey, group_id=group.id, interval=interval)