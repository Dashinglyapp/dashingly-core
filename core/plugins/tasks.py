from core.plugins.scope import TaskScope

class TaskBase(object):
    name = None
    task_proxy = None
    manager = None
    scope = TaskScope(zone="group")

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def run(self):
        raise NotImplementedError

class Interval(object):
    hourly = 60 * 60
    daily = 24 * hourly
    weekly = 7 * daily
    monthly = 4 * weekly