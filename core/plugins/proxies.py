from core.database.models import TimePoint, Blob

class MetricProxy(object):
    def __init__(self, name):
        self.name = name

class SourceProxy(object):
    def __init__(self, name):
        self.name = name

class PluginProxy(object):
    def __init__(self, name, hashkey):
        self.name = name
        self.hashkey = hashkey

class PluginModelProxy(object):
    def __init__(self, plugin_id, metric_id, name):
        self.plugin_id = plugin_id
        self.metric_id = metric_id
        self.name = name

class TaskProxy(object):
    def __init__(self, name):
        self.name = name