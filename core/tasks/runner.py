from app import celery
from core.database.models import User, Plugin
from core.manager import ExecutionContext
from core.tasks.manager import TaskManager

@celery.task()
def run_delayed(user_id, plugin_hashkey, interval=None):
    from core.plugins.loader import plugins
    user = User.filter(User.id == user_id).first()
    plugin = plugins[plugin_hashkey]
    context = ExecutionContext(user=user, plugin=plugin)
    manager = TaskManager(context)

    tasks = plugin.tasks
    for task in tasks:
        if task.interval == interval:
            manager.run(task)

def interval_task():
    pass