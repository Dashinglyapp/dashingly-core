from flask.ext.login import current_user
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.security.utils import encrypt_password
from wtforms import PasswordField
from core.database.models import User, Plugin, UserProfile, Group, PluginData

class AuthMixin(object):
    def is_accessible(self):
        # Change this to do an admin check.
        return current_user.has_role('admin')

class IndexView(AuthMixin, BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class UserView(AuthMixin, ModelView):
    can_create = True
    form_excluded_columns = ('password', 'profile', 'hashkey', 'plugindata', 'metrics', 'sources', 'authorizations', 'created', 'updated', 'resourcedata', 'owned_groups', )
    column_list = ('email', 'username', )
    column_searchable_list = ('email', 'username', )
    model = User

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(self.model, session, **kwargs)

    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model):
        if len(model.password2):
            model.password = encrypt_password(form.password2.data)


class UserProfileView(AuthMixin, ModelView):
    can_create = False
    model = UserProfile
    def __init__(self, session, **kwargs):
    # You can pass name and other parameters if you want to
        super(UserProfileView, self).__init__(self.model, session, **kwargs)


class PluginView(AuthMixin, ModelView):
    can_create = False
    form_excluded_columns = ('name', 'hashkey', 'created', 'updated', 'pluginmodels', 'plugindata',)
    column_list = ('name', 'hashkey', 'description', )
    column_searchable_list = ('name', 'hashkey', )
    model = Plugin

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(PluginView, self).__init__(self.model, session, **kwargs)

class GroupView(AuthMixin, ModelView):
    can_create = True
    form_excluded_columns = ('hashkey', 'created', 'updated', 'profile', 'plugindata', 'resourcedata', )
    column_list = ('name', 'hashkey', )
    column_searchable_list = ('name', 'hashkey', )
    model = Group

    def __init__(self, session, **kwargs):
    # You can pass name and other parameters if you want to
        super(GroupView, self).__init__(self.model, session, **kwargs)

class PluginDataView(AuthMixin, ModelView):
    can_create = True
    form_excluded_columns = ('hashkey', 'created', 'updated', )
    column_list = ('plugin_id', 'metric_id', 'hashkey', 'user', )
    column_searchable_list = ('plugin_id', 'metric_id', 'hashkey', )
    model = PluginData

    def __init__(self, session, **kwargs):
    # You can pass name and other parameters if you want to
        super(PluginDataView, self).__init__(self.model, session, **kwargs)
