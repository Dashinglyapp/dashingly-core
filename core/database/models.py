import hashlib
from sqlalchemy import event
from realize.log import logging
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin

log = logging.getLogger(__name__)
db = SQLAlchemy()

STRING_MAX = 255

user_plugins = db.Table('user_plugins', db.Model.metadata,
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('plugin_id', db.Integer, db.ForeignKey('plugins.id'))
)

user_metrics = db.Table('user_metrics', db.Model.metadata,
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('metric_id', db.Integer, db.ForeignKey('metrics.id'))
)

user_sources = db.Table('user_sources', db.Model.metadata,
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('source_id', db.Integer, db.ForeignKey('sources.id'))
)

user_groups = db.Table('user_groups', db.Model.metadata,
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

roles_users = db.Table('roles_users', db.Model.metadata,
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(STRING_MAX), unique=True)
    description = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Role(name='%s')>" % (self.name)

class User(db.Model, UserMixin):
    hash_vals = ["username", "email"]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(STRING_MAX), unique=True)
    email = db.Column(db.String(STRING_MAX), unique=True)
    password = db.Column(db.String(STRING_MAX))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(timezone=True))
    hashkey = db.Column(db.String(STRING_MAX), unique=True)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    profile = db.relationship("UserProfile", uselist=False, backref="user")
    plugins = db.relationship('Plugin', secondary=user_plugins, backref='users')
    metrics = db.relationship('Metric', secondary=user_metrics, backref='users')
    sources = db.relationship('Source', secondary=user_sources, backref='users')
    groups = db.relationship('Group', secondary=user_groups, backref='users')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "<User(name='%s', email='%s', password='%s')>" % (self.username, self.email, self.password)

class UserProfile(db.Model):
    __tablename__ = 'userprofile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    first_name = db.Column(db.String(STRING_MAX))
    last_name = db.Column(db.String(STRING_MAX))
    timezone = db.Column(db.Text)
    settings = db.Column(db.Text)

    def __repr__(self):
        return "<UserProfile(id='%s', user_id='%s')>" % (self.id, self.user_id)

class Authorization(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'name'), )
    hash_vals = ["name"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    access_token = db.Column(db.String(STRING_MAX))
    refresh_token = db.Column(db.String(STRING_MAX))
    expires_in = db.Column(db.String(STRING_MAX))

    user = db.relationship("User", backref=db.backref('authorizations', order_by=id))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

class UserItem(db.Model):
    __tablename__ = 'useritem'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    type = db.Column(db.String(50))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity':'useritem',
        'polymorphic_on':type
    }

    def __repr__(self):
        return "<UserItem(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)


class Plugin(UserItem):
    __tablename__ = 'plugins'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )
    __mapper_args__ = {
        'polymorphic_identity':'plugins',
        }

    id = db.Column(db.Integer, db.ForeignKey('useritem.id'), primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Plugin(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class Metric(UserItem):
    __tablename__ = 'metrics'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )
    __mapper_args__ = {
        'polymorphic_identity':'metrics',
        }
    hash_vals = ["name"]

    id = db.Column(db.Integer, db.ForeignKey('useritem.id'), primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Metric(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class Source(UserItem):
    __tablename__ = 'sources'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )
    __mapper_args__ = {
        'polymorphic_identity':'sources',
        }
    hash_vals = ["name"]

    id = db.Column(db.Integer, db.ForeignKey('useritem.id'), primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Source(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class Group(UserItem):
    __tablename__ = 'groups'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )
    __mapper_args__ = {
        'polymorphic_identity': 'groups',
        }
    hash_vals = ["name"]

    id = db.Column(db.Integer, db.ForeignKey('useritem.id'), primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Group(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class PluginModel(db.Model):
    __tablename__ = 'pluginmodels'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name', 'plugin_id'), db.UniqueConstraint('metric_id', 'plugin_id'), )
    hash_vals = ["plugin_id", "metric_id", "name"]

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))
    plugin_id = db.Column(db.String(STRING_MAX), db.ForeignKey('plugins.hashkey'))
    metric_id = db.Column(db.String(STRING_MAX), db.ForeignKey('metrics.name'))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    plugin = db.relationship("Plugin", backref=db.backref('pluginmodels', order_by=id))
    metric = db.relationship("Metric", backref=db.backref('pluginmodels', order_by=id))

    def __repr__(self):
        return "<PluginModel(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class WidgetModel(db.Model):
    __tablename__ = "widgetmodels"
    __table_args__ = (db.UniqueConstraint('hashkey'), )
    hash_vals = ["name"]

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))
    settings = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref('widgetmodels', order_by=id))
    group = db.relationship("Group", backref=db.backref('widgetmodels', order_by=id))

    def __repr__(self):
        return "<WidgetModel(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class PluginData(db.Model):
    __tablename__ = 'plugindata'
    __table_args__ = (db.UniqueConstraint("plugin_id", "metric_id", "user_id", "hashkey"), )
    hash_vals = ["plugin_id", "metric_id", "user_id", "date", "data"]

    id = db.Column(db.Integer, primary_key=True)
    plugin_id = db.Column(db.String(STRING_MAX), db.ForeignKey('plugins.hashkey'))
    metric_id = db.Column(db.String(STRING_MAX), db.ForeignKey('metrics.name'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    source_id = db.Column(db.String(STRING_MAX), db.ForeignKey("sources.name"))
    plugin_model_id = db.Column(db.String(STRING_MAX), db.ForeignKey("pluginmodels.hashkey"))
    date = db.Column(db.DateTime(timezone=True))

    data = db.Column(db.Text)

    user = db.relationship("User", backref=db.backref('plugindata', order_by=id))
    group = db.relationship("Group", backref=db.backref('plugindata', order_by=id))
    plugin = db.relationship("Plugin", backref=db.backref('plugindata', order_by=id))
    plugin_model = db.relationship("PluginModel", backref=db.backref('plugindata', order_by=id))
    metric = db.relationship("Metric", backref=db.backref('plugindata', order_by=id))
    source = db.relationship("Source", backref=db.backref('plugindata', order_by=id))

    hashkey = db.Column(db.String(STRING_MAX))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)
    def __repr__(self):
        return "<Data(plugin='%s', metric='%s')>" % (self.plugin_id, self.metric_id)

# Create hashkeys to make items unique

def make_hash(vals):
    mhash = hashlib.md5()
    for v in vals:
        try:
            mhash.update(str(v))
        except Exception:
            log.info("Could not hash value {1}".format(v))
            continue

    hashkey = mhash.hexdigest()
    return hashkey

def add_hashkey(mapper, connection, target):
    target.hashkey = make_hash([getattr(target, k) for k in target.hash_vals])

def add_profile(mapper, connection, target):
    target.profile = UserProfile()

# Register hashkey adding events.
event.listen(PluginData, "before_insert", add_hashkey)
event.listen(PluginModel, "before_insert", add_hashkey)
event.listen(User, "before_insert", add_hashkey)
event.listen(Group, "before_insert", add_hashkey)
event.listen(Metric, "before_insert", add_hashkey)
event.listen(Source, "before_insert", add_hashkey)
event.listen(WidgetModel, "before_insert", add_hashkey)
event.listen(User, "before_insert", add_profile)