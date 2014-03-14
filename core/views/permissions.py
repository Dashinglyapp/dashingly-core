from core.manager import BaseManager, ExecutionContext
from core.permissions import BasePermissions
from core.resources.permissions import ResourcePermissionsManager
from flask.ext.login import current_user

class ViewPermissionsManager(BasePermissions):

    def check_perms(self, obj, perm_type, resource_hashkey):
        from app import db
        from core.database.models import ResourceData
        authed = False
        if self.req_user is not None:
            authed = self.check_user_perms(obj, perm_type)
        elif self.req_group is not None:
            authed = self.check_group_perms(obj, perm_type)

        if not authed and resource_hashkey is not None:
            context = ExecutionContext(plugin=self.plugin, user=current_user)
            resource_permissions = ResourcePermissionsManager(context)
            resource = db.session.query(ResourceData).filter_by(hashkey=resource_hashkey).first()
            authed = resource_permissions.check_perms(resource, perm_type)
        return authed

    def check_user_perms(self, obj, perm_type):
        if self.req_user == current_user:
            return True
        return False

    def check_group_perms(self, obj, perm_type):
        if self.req_group.owner == current_user:
            return True
        return False


