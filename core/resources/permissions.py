from core.permissions import BasePermissions
from core.util import InvalidScopeException


class ResourcePermissionsManager(BasePermissions):

    def get_user(self, hashkey):
        from app import db
        from core.database.models import User
        return db.session.query(User).filter_by(hashkey=hashkey).first()

    def get_group(self, hashkey):
        from app import db
        from core.database.models import Group
        return db.session.query(Group).filter_by(hashkey=hashkey).first()

    def check_perms(self, obj, perm_type):
        if obj.user is not None:
            return self.check_user_perms(obj, perm_type)
        elif obj.group is not None:
            return self.check_group_perms(obj, perm_type)
        else:
            raise InvalidScopeException()

    def check_view_permissions(self, obj):
        for p in obj.permissions:
            if p.public:
                return True
            if p.owner_scope == "user":
                if p.owner_hashkey is not None and self.req_user.hashkey == p.owner_hashkey:
                    return True
            elif p.owner_scope == "group":
                if p.owner_hashkey is not None:
                    group = self.get_group(p.owner_hashkey)
                    if group is not None and group in self.req_user.groups:
                        return True
        return False

    def check_user_perms(self, obj, perm_type):
        user = obj.user
        if self.req_user == user:
            return True
        if perm_type == "view":
            return self.check_view_permissions(obj)
        return False

    def check_group_perms(self, obj, perm_type):
        group = obj.group
        if group.owner == self.req_user:
            return True

        if perm_type == "view" and group in self.req_user.groups:
            return True
        elif perm_type == "view":
            return self.check_view_permissions(obj)

        return False

