import hashlib
from flask import url_for, jsonify
from core.manager import BaseManager
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
        views = []
        for v in plugin.views:
            views += dfs(v)

        view_dict = {}
        for i in xrange(len(views)):
            view = views[i]
            view.hashkey = hashlib.sha224("{0}{1}".format(plugin.hashkey, view.name)).hexdigest()[:VIEW_HASHKEY_LENGTH]
            view_route = "views/{0}".format(view.hashkey)

            # Cannot use url_for here, because it needs to be called in celery tasks, and celery doesn't have a request to use
            # to make a URL.  Could fix by specifying server_name, but that seems to heavyweight for now.
            plugin_path = '/api/v1/plugins/{0}/{1}'.format(plugin.hashkey, view_route)
            view.path = plugin_path
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
        return view_cls.meta()

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
