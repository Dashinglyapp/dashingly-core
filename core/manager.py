class BaseManager(object):
    def __init__(self, context, **kwargs):
        self.user = context.user
        self.plugin = context.plugin
        self.group = context.group
        self.user_inst = True
        self.group_inst = True

        self.context = context

        self.all_inst = False
        if self.user is None:
            self.user_inst = False

        if self.group is None:
            self.group_inst = False

        if self.user_inst:
            self.group_inst = False

        if not self.user_inst and not self.group_inst:
            self.all_inst = True

    def get_manager_from_hashkey(self, plugin_hashkey):
        plugin = self.lookup_plugin(plugin_hashkey)
        return self.get_manager_from_plugin(plugin)

    def get_manager_from_plugin(self, plugin):
        from app import db
        from core.database.manager import DBManager
        context = ExecutionContext(user=self.user, plugin=plugin, group=self.group)
        manager = DBManager(context, session=db.session)
        return manager

    def get_manager_from_context(self):
        from core.database.models import Plugin

        plugin = self.plugin
        if not isinstance(self.plugin, Plugin):
            plugin = self.lookup_plugin(self.plugin.hashkey)

        return self.get_manager_from_plugin(plugin)

    def lookup_plugin(self, plugin_hashkey):
        from core.database.models import Plugin
        from app import db
        return db.session.query(Plugin).filter(Plugin.hashkey == plugin_hashkey).first()

    def get_plugin(self, plugin_hashkey):
        from core.plugins.loader import plugins
        plugin_cls = plugins[plugin_hashkey]
        return plugin_cls

class ExecutionContext(object):
    def __init__(self, user=None, plugin=None, group=None):
        self.user = user
        self.plugin = plugin
        self.group = group