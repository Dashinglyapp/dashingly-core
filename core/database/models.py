import hashlib
from sqlalchemy import event
import logging
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin
from app import app
import settings

log = logging.getLogger(__name__)
db = SQLAlchemy(app)

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

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(STRING_MAX))
    last_name = db.Column(db.String(STRING_MAX))
    username = db.Column(db.String(STRING_MAX), unique=True)
    email = db.Column(db.String(STRING_MAX), unique=True)
    password = db.Column(db.String(STRING_MAX))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(timezone=True))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    plugins = db.relationship('Plugin', secondary=user_plugins, backref='users')
    metrics = db.relationship('Metric', secondary=user_metrics, backref='users')
    sources = db.relationship('Source', secondary=user_sources, backref='users')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "<User(name='%s', lastname='%s', password='%s')>" % (self.username, self.last_name, self.password)

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

    id = db.Column(db.Integer, db.ForeignKey('useritem.id'), primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Source(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class PluginModel(db.Model):
    __tablename__ = 'pluginmodels'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )
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

class Data(db.Model):
    __tablename__ = 'data'
    __table_args__ = (db.Index('unique_hash_time', "plugin_id", "metric_id", "user_id", "hashkey"), db.UniqueConstraint('hashkey'), )

    hash_vals = ["plugin_id", "metric_id", "user_id", "data", "date"]

    id = db.Column(db.Integer, primary_key=True)
    plugin_id = db.Column(db.String(STRING_MAX), db.ForeignKey('plugins.hashkey'))
    metric_id = db.Column(db.String(STRING_MAX), db.ForeignKey('metrics.name'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    source_id = db.Column(db.String(STRING_MAX), db.ForeignKey("sources.name"))
    plugin_model_id = db.Column(db.String(STRING_MAX), db.ForeignKey("pluginmodels.hashkey"))
    date = db.Column(db.DateTime(timezone=True))
    type = db.Column(db.String(50))

    hashkey = db.Column(db.String(STRING_MAX))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    modified = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity':'data',
        'polymorphic_on':type
    }

    def __repr__(self):
        return "<Data(plugin='%s', metric='%s')>" % (self.plugin_id, self.metric_id)

class TimePoint(Data):
    __tablename__ = 'timepoints'
    __mapper_args__ = {
        'polymorphic_identity':'timepoints',
        }

    id = db.Column(db.Integer, db.ForeignKey('data.id'), primary_key=True)
    data = db.Column(db.String(STRING_MAX))

    user = db.relationship("User", backref=db.backref('timepoints', order_by=id))
    plugin = db.relationship("Plugin", backref=db.backref('timepoints', order_by=id))
    plugin_model = db.relationship("PluginModel", backref=db.backref('timepoints', order_by=id))
    metric = db.relationship("Metric", backref=db.backref('timepoints', order_by=id))
    source = db.relationship("Source", backref=db.backref('timepoints', order_by=id))

    def __repr__(self):
        return "<TimePoints(plugin='%s', metric='%s', data='%s')>" % (self.plugin_id, self.metric_id, self.data)

class Blob(Data):
    __tablename__ = 'blobs'
    __mapper_args__ = {
        'polymorphic_identity':'blobs',
        }

    id = db.Column(db.Integer, db.ForeignKey('data.id'), primary_key=True)
    data = db.Column(db.Text)

    user = db.relationship("User", backref=db.backref('blobs', order_by=id))
    plugin = db.relationship("Plugin", backref=db.backref('blobs', order_by=id))
    plugin_model = db.relationship("PluginModel", backref=db.backref('blobs', order_by=id))
    metric = db.relationship("Metric", backref=db.backref('blobs', order_by=id))
    source = db.relationship("Source", backref=db.backref('blobs', order_by=id))

    def __repr__(self):
        return "<Blobs(plugin='%s', metric='%s', data='%s')>" % (self.plugin_id, self.metric_id, self.data)

# Create hashkeys to make items unique

def make_hash(vals):
    mhash = hashlib.md5()
    for v in vals:
        try:
            mhash.update(str(v))
        except Exception:
            log.info("Could not hash vale {1}".format(v))
            continue

    hashkey = mhash.hexdigest()
    return hashkey

def add_hashkey(mapper, connection, target):
    target.hashkey = make_hash([getattr(target, k) for k in target.hash_vals])

# Register hashkey adding events.
event.listen(TimePoint, "before_insert", add_hashkey)
event.listen(Blob, "before_insert", add_hashkey)
event.listen(PluginModel, "before_insert", add_hashkey)