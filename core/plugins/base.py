from proxies import PluginProxy

class BasePlugin(object):
    name = None
    hashkey = None
    routes = []
    forms = []
    models = []
    views = []
    permissions = []

    def __init__(self, context, manager):

        self.user = manager.user
        self.plugin = context.plugin
        self.plugin_proxy = PluginProxy(
            name=context.plugin.name,
            hashkey=context.plugin.hashkey
        )
        self.context = context
        self.manager = manager

    def setup(self):
        """
        Put setup actions here.
        """
        pass

    def upgrade(self):
        """
        Put upgrade actions here.
        """
        pass

    def destroy(self):
        pass

    def save_forms(self, metric, **kwargs):
        pass