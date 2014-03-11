from core.manager import BaseManager


class GroupPermissions(BaseManager):
    def check_view_perms(self, obj):
        return obj in self.user.groups

    def check_update_perms(self, obj):
        return self.user == obj.owner

    def check_delete_perms(self, obj):
        return self.check_update_perms(obj)

    def check_perms(self, obj, perm_type):
        if perm_type == "view":
            return self.check_view_perms(obj)
        elif perm_type == "update":
            return self.check_update_perms(obj)
        elif perm_type == "delete":
            return self.check_delete_perms(obj)
