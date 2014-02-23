from proxies import PluginProxy

class BasePlugin(object):
    name = None

    def __init__(self, context, wrapper):
        self.context = context

        self.user = context.user
        self.plugin = context.plugin
        self.plugin_proxy = PluginProxy(
            name=context.plugin.name,
            hashkey=context.plugin.hashkey
        )
        self.wrapper = wrapper

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