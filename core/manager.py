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

    def get_manager_for_context(self):
        from app import db
        from core.database.manager import DBManager
        from core.database.models import Plugin

        plugin = self.plugin
        if not isinstance(self.plugin, Plugin):
            plugin = self.lookup_plugin(self.plugin.hashkey)

        context = ExecutionContext(user=self.user, plugin=plugin, group=self.group)
        manager = DBManager(context, session=db.session)
        return manager

    def lookup_plugin(self, plugin_hashkey):
        from core.database.models import Plugin
        from app import db
        return db.session.query(Plugin).filter(Plugin.hashkey == plugin_hashkey).first()


class ExecutionContext(object):
    def __init__(self, user=None, plugin=None, group=None):
        self.user = user
        self.plugin = plugin
        self.group = group