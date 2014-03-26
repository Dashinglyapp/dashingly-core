from flask.ext.login import current_user
from core.database.models import ResourceData, Permission
from core.manager import BaseManager, ExecutionContext
from core.resources.permissions import ResourcePermissionsManager
from core.util import get_context_for_scope, IncorrectPermissionsException
import json
from flask import current_app

class InvalidScopeException(Exception):
    pass

class ResourceManager(BaseManager):

    def get_view(self, view_hashkey):
        from app import db
        from core.database.models import PluginView
        return db.session.query(PluginView).filter(PluginView.hashkey == view_hashkey).first()

    def create_permission(self, scope, public, key):
        from app import db
        from core.database.models import User, Group
        model = Permission()
        if scope == "user":
            if key is not None:
                model.user = db.session.query(User).filter_by(id=key).first()
        elif scope == "group":
            if key is not None:
                model.group = db.session.query(Group).filter_by(id=key).first()
        else:
            raise InvalidScopeException()
        model.scope = scope
        model.public = public
        db.session.add(model)
        db.session.commit()
        print model.user
        print model.group
        return model

    def check_permissions(self, obj, perm_type):
        context = ExecutionContext(user=current_user)
        permissions = ResourcePermissionsManager(context)
        return permissions.check_perms(obj, perm_type)

    def get_or_create_model(self, **kwargs):
        from app import db
        hashkey = kwargs.pop('hashkey', None)
        if hashkey is not None:
            return db.session.query(ResourceData).filter_by(hashkey=hashkey).first()
        else:
            return self.create_model(**kwargs)

    def create_model(self, **kwargs):
        from app import db
        views = kwargs.pop('views', None)
        permissions = kwargs.pop('permissions', None)
        related = kwargs.pop('related', None)
        model = ResourceData(
            user=self.user,
            group=self.group,
            version=current_app.config['RESOURCE_DATA_VERSION'],
            **kwargs
        )
        db.session.add(model)
        if views is not None:
            for v in views:
                view = self.get_view(v)
                if view is not None:
                    model.views.append(view)
        if permissions is not None:
            for p in permissions:
                model.permissions.append(self.create_permission(p['scope'], p['public'], p['hashkey']))
        db.session.commit()
        return model

    def get_model(self, resource_hashkey):
        from app import db
        model = db.session.query(ResourceData).filter(ResourceData.hashkey == resource_hashkey).first()
        if not self.check_permissions(model, "view"):
            raise IncorrectPermissionsException()
        if model is not None:
            model_settings = model.settings
            if model_settings is None:
                model_settings = {}
            return model, model_settings
        return None, None

    def update_model(self, resource_hashkey, data):
        from app import db
        model, model_settings = self.get_model(resource_hashkey)
        if not self.check_permissions(model, "update"):
            raise IncorrectPermissionsException()
        views = data.pop('views', None)
        permissions = data.pop('permissions', None)
        related = data.pop('related', None)
        for k in data:
            if k == "settings":
                try:
                    data[k] = json.loads(data[k])
                except Exception:
                    pass
                for d in data[k]:
                    model_settings[d] = data[k][d]
                model.settings = model_settings
            else:
                setattr(model, k, data[k])
        if views is not None:
            view_objs = []
            for v in views:
                view_objs.append(self.get_view(v))
            model.views = view_objs

        if permissions is not None:
            perm_objs = []
            for p in permissions:
                perm_objs.append(self.create_permission(p['scope'], p['public'], p['hashkey']))
            model.permissions = perm_objs

        if related is not None:
            related_objs = []
            for r in related:
                related_objs.append(self.get_or_create_model(**r))
            model.related = related_objs

        db.session.commit()
        return model

    def delete_model(self, resource_hashkey):
        from app import db
        model, model_settings = self.get_model(resource_hashkey)
        if not self.check_permissions(model, "delete"):
            raise IncorrectPermissionsException()
        db.session.delete(model)
        db.session.commit()

    def get_resource(self, resource_hashkey):
        return self.get_model(resource_hashkey)

    def create_resource(self, **kwargs):
        return self.create_model(**kwargs)

    def update_resource(self, resource_hashkey, data):
        return self.update_model(resource_hashkey, data)

    def delete_resource(self, resource_hashkey):
        return self.delete_model(resource_hashkey)


