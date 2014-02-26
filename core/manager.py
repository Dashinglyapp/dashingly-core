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

class ExecutionContext(object):
    def __init__(self, user=None, plugin=None, group=None):
        self.user = user
        self.plugin = plugin
        self.group = group