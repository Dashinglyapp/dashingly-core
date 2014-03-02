from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm
from core.manager import BaseManager
from realize.log import logging

log = logging.getLogger(__name__)

class InvalidPermissionsException(Exception):
    pass

class InvalidModelException(Exception):
    pass

class PermissionsManager(BaseManager):
    def __init__(self, context):
        super(PermissionsManager, self).__init__(context)
        self.req_user = self.user
        self.req_group = self.group
        self.req_plugin = self.plugin

    def check_update_perms_user(self, perms, obj):
        return self.user_inst and obj.user == self.req_user

    def check_update_perms_group(self, perms, obj):
        return self.group_inst and obj.group == self.req_group

    def check_update_perms(self, perms, obj):
        if obj.plugin == self.req_plugin:
            if self.user_inst:
                return self.check_update_perms_user(perms, obj)
            elif self.group_inst:
                return self.check_update_perms_group(perms, obj)
        return False

    def check_delete_perms(self, perms, obj):
        if obj.plugin == self.req_plugin:
            if self.user_inst:
                return self.check_update_perms_user(perms, obj)
            elif self.group_inst:
                return self.check_update_perms_group(perms, obj)
        return False

    def check_view_perms(self, perms, obj):
        for p in perms:
            allowed = self.check_perm(p, obj, obj.plugin)
            if allowed:
                return True
        return False

    def check_perms(self, obj, perm_type):
        from core.plugins.loader import plugins
        default_scope = [Scope(ZonePerm("user", "current"), BlockPerm("plugin", "current"))]

        plugin = obj.plugin

        plugin_cls = plugins[plugin.hashkey]
        plugin_model_cls = None
        for m in plugin_cls.models:
            if m.plugin_model_proxy.hashkey == obj.plugin_model.hashkey:
                plugin_model_cls = m

        if plugin_model_cls is None:
            raise InvalidModelException()

        perms = getattr(plugin_model_cls, "perms")
        if not isinstance(perms, list):
            perms = default_scope

        if perm_type == "view":
            return self.check_view_perms(perms, obj)
        elif perm_type == "update":
            return self.check_update_perms(perms, obj)
        elif perm_type == "delete":
            return self.check_delete_perms(perms, obj)

        return False

    def check_perm(self, perm, obj, plugin):
        zone = perm.zone
        block = perm.block

        if not isinstance(zone, ZonePerm) or not isinstance(block, BlockPerm):
            raise InvalidPermissionsException()

        zone_perm = self.check_zone_perm(zone, obj)
        block_perm = self.check_block_perm(block, plugin)

        return zone_perm and block_perm

    def check_zone_perm_user(self, zone, obj):
        if zone.scope == "user":
            if zone.key is not None and zone.key == self.req_user.hashkey:
                return True
            elif zone.all:
                return True
            elif zone.current and obj.user == self.req_user:
                return True
            else:
                return False
        elif zone.scope == "group":
            user_group_keys = [g.hashkey for g in self.req_user.groups]
            if zone.key is not None:
                if zone.key in user_group_keys:
                    return True
            elif zone.all:
                owner_group_keys = [g.hashkey for g in obj.user.groups]
                if len(set(user_group_keys).intersection(owner_group_keys)) > 0:
                    return True
            else:
                return False

        return False

    def check_zone_perm_group(self, zone, obj):
        if zone.scope == "group":
            if zone.key is not None:
                if zone.key == self.req_group.hashkey:
                    return True
            elif zone.all:
                owner_group_keys = [g.hashkey for g in obj.user.groups]
                if self.req_group.hashkey in owner_group_keys:
                    return True
            else:
                return False

        return False

    def check_zone_perm_all(self, zone, obj):
        if zone.scope == "user" and zone.all:
            return True
        elif zone.scope == "group" and zone.all:
            return True

        return False

    def check_zone_perm(self, zone, obj):
        if self.user_inst:
            return self.check_zone_perm_user(zone, obj)
        elif self.group_inst:
            return self.check_zone_perm_group(zone, obj)
        elif self.all_inst:
            return self.check_zone_perm_all(zone, obj)
        return False

    def check_block_perm(self, block, plugin):
        if block.scope == "plugin":
            if block.key is not None and block.key == self.req_plugin.hashkey:
                return True
            elif block.all:
                return True
            elif block.current and plugin.hashkey == self.req_plugin.hashkey:
                return True
            else:
                return False

        return False


