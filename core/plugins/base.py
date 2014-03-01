from proxies import PluginProxy

class BasePlugin(object):
    name = None
    hashkey = None
    routes = []
    forms = []
    models = []
    views = []
    permissions = []
    settings_form = None

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
        for form_cls in self.forms:
            if form_cls.metric_proxy.name == metric.name:
                form = form_cls(**kwargs)
                form.manager = self.manager
                form.context = self.context
                if form.validate():
                    form.save()

    def save_settings(self, **kwargs):
        if self.settings_form is not None:
            form = self.settings_form(**kwargs)
            form.manager = self.manager
            form.context = self.context
            if form.validate():
                form.save()