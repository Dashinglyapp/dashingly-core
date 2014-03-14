from core.manager import BaseManager


class BasePermissions(BaseManager):
    def __init__(self, context):
        super(BasePermissions, self).__init__(context)

        self.req_user = self.user
        self.req_group = self.group
        self.req_plugin = self.plugin