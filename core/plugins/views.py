import hashlib
from flask import url_for, jsonify
from core.manager import BaseManager
from core.util import api_url_for
from realize.settings import VIEW_HASHKEY_LENGTH

def dfs(v):
    visited = []
    visited.append(v)
    for w in v.children:
        if w not in visited:
            visited += dfs(w)
    return visited

class ViewManager(BaseManager):
    def set_hashkeys(self, plugin):

        view_dict = {}
        for i in xrange(len(plugin.views)):
            view = plugin.views[i]
            view.hashkey = hashlib.sha224("{0}{1}".format(plugin.hashkey, view.name)).hexdigest()[:VIEW_HASHKEY_LENGTH]
            view_dict[view.hashkey] = view
        plugin.view_dict = view_dict

    def handle_route(self, hashkey, method, data):
        view_dict = self.get_plugin(self.plugin.hashkey).view_dict
        view_cls = view_dict[hashkey]
        manager = self.get_manager_from_context()
        view = view_cls()
        view.context = self.context
        view.manager = manager
        func = getattr(view, method)
        return jsonify(func(data))

    def get_meta(self, hashkey):
        view_dict = self.get_plugin(self.plugin.hashkey).view_dict
        view_cls = view_dict[hashkey]
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
