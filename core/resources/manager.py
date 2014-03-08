from flask.ext.login import current_user
from core.database.models import ResourceData
from core.manager import BaseManager, ExecutionContext
from core.resources.permissions import ResourcePermissionsManager
from core.util import get_context_for_scope, IncorrectPermissionsException
import json
from realize import settings


class ResourceManager(BaseManager):

    def check_permissions(self, obj, perm_type):
        context = ExecutionContext(user=current_user)
        permissions = ResourcePermissionsManager(context)
        return permissions.check_perms(obj, perm_type)

    def create_model(self, settings_dict, name, type):
        from app import db
        model = ResourceData(
            user=current_user,
            name=name,
            version=settings.RESOURCE_DATA_VERSION,
            type=type,
            settings=json.dumps(settings_dict)
        )
        db.session.add(model)
        db.session.commit()
        return model

    def get_model(self, resource_hashkey):
        from app import db
        model = db.session.query(ResourceData).filter(ResourceData.hashkey == resource_hashkey).first()
        if not self.check_permissions(model, "view"):
            raise IncorrectPermissionsException()
        if model is not None:
            try:
                model_settings = json.loads(model.settings)
            except ValueError:
                model_settings = {}
            except TypeError:
                model_settings = {}
            return model, model_settings
        return None, None

    def update_model(self, resource_hashkey, data):
        from app import db
        model, model_settings = self.get_model(resource_hashkey)
        if not self.check_permissions(model, "update"):
            raise IncorrectPermissionsException()
        for d in data:
            model_settings[d] = data[d]
        model.settings = model_settings
        db.commit()
        return model

    def delete_model(self, resource_hashkey):
        from app import db
        model, model_settings = self.get_model(resource_hashkey)
        if not self.check_permissions(model, "delete"):
            raise IncorrectPermissionsException()
        model.settings = json.dumps({})
        db.commit()

    def get_resource(self, resource_hashkey):
        return self.get_model(resource_hashkey)

    def create_resource(self, settings, name, type):
        return self.create_model(settings, name, type)

    def update_resource(self, resource_hashkey, data):
        return self.update_model(resource_hashkey, data)

    def delete_resource(self, resource_hashkey):
        return self.delete_model(resource_hashkey)


