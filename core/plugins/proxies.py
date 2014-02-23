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

class TimePointProxy(object):
    pass
