import hashlib
from flask import url_for, jsonify
from core.manager import BaseManager
from core.plugins.lib.proxies import PluginViewProxy
from core.util import api_url_for, get_cls
from core.database.models import PluginView
from core.views.permissions import ViewPermissionsManager


class InvalidViewException(Exception):
    pass

class NotAuthorizedException(Exception):
    pass

def dfs(v):
    visited = []
    visited.append(v)
    for w in v.children:
        if w not in visited:
            visited += dfs(w)
    return visited

class ViewManager(BaseManager):
    perm_types = {
        'post': 'create',
        'get': 'view',
        'put': 'update',
        'patch': 'update',
        'delete': 'delete'
    }

    def register_views(self, plugin):
        for view in plugin.views:
            self.register_view_model(plugin, view)

    def register_view_model(self, plugin_cls, model):
        from app import db
        proxy = PluginViewProxy(
            plugin_id=plugin_cls.hashkey,
            name=model.name
        )
        val = get_cls(db.session, PluginView, proxy, attrs=["name", "plugin_id"], create=True)
        proxy.hashkey = val.hashkey
        model.plugin_view_proxy = proxy
        model.hashkey = val.hashkey

    def get_view_cls(self, hashkey):
        plugin = self.get_plugin(self.plugin.hashkey)
        for v in plugin.views:
            if v.hashkey == hashkey:
                return v
        raise InvalidViewException()

    def check_permissions(self, hashkey, method, resource_hashkey):
        from app import db
        from core.database.models import PluginView
        view = db.session.query(PluginView).filter_by(hashkey=hashkey).first()

        permissions = ViewPermissionsManager(self.context)
        return permissions.check_perms(view, self.perm_types[method], resource_hashkey)

    def handle_route(self, hashkey, method, data, resource_hashkey):
        view_cls = self.get_view_cls(hashkey)
        manager = self.get_manager_from_context()
        view = view_cls()
        view.context = self.context
        view.manager = manager
        func = getattr(view, method)
        return jsonify(func(data))

    def get_meta(self, hashkey):
        view_cls = self.get_view_cls(hashkey)
        meta = view_cls.meta()
        return meta

    def get_settings(self, plugin_hashkey, data):
        plugin_cls = self.get_plugin(plugin_hashkey)
        manager = self.get_manager_from_hashkey(plugin_hashkey)
        if plugin_cls.settings_form is None:
            return jsonify({})

        obj_cls = plugin_cls.settings_form.model
        obj = obj_cls()
        obj = manager.get_or_create(obj, query_data=False)
        form = plugin_cls.settings_form()
        for f in form:
            setattr(form, f.name, getattr(obj, f.name, None))

        return jsonify(form.as_json())

