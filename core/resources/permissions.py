from core.manager import BaseManager
from core.util import InvalidScopeException


class ResourcePermissionsManager(BaseManager):
    def __init__(self, context):
        super(ResourcePermissionsManager, self).__init__(context)
        self.req_user = self.user
        self.req_group = self.group

    def check_perms(self, obj, perm_type):
        if obj.user is not None:
            return self.check_user_perms(obj)
        elif obj.group is not None:
            return self.check_group_perms(obj)
        else:
            raise InvalidScopeException()

    def check_user_perms(self, obj):
        if self.req_user == obj.user:
            return True
        return False

    def check_group_perms(self, obj):
        group = obj.group
        if group in self.req_user.groups:
            return True
        return False

