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
    confirmed_at = db.Column(db.DateTime())

    created = db.Column(db.Date, default=datetime.now)
    updated = db.Column(db.Date, onupdate=datetime.now)

    plugins = db.relationship('Plugin', secondary=user_plugins, backref='users')
    metrics = db.relationship('Metric', secondary=user_metrics, backref='users')
    sources = db.relationship('Source', secondary=user_sources, backref='users')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "<User(name='%s', lastname='%s', password='%s')>" % (self.username, self.last_name, self.password)

class Plugin(db.Model):
    __tablename__ = 'plugins'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))
    version = db.Column(db.Integer)

    created = db.Column(db.Date, default=datetime.now)
    updated = db.Column(db.Date, onupdate=datetime.now)

    def __repr__(self):
        return "<Plugin(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class Metric(db.Model):
    __tablename__ = 'metrics'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))
    version = db.Column(db.Integer)

    created = db.Column(db.Date, default=datetime.now)
    updated = db.Column(db.Date, onupdate=datetime.now)

    def __repr__(self):
        return "<Metric(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class Source(db.Model):
    __tablename__ = 'sources'
    __table_args__ = (db.UniqueConstraint('hashkey'), db.UniqueConstraint('name'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    hashkey = db.Column(db.String(STRING_MAX))
    version = db.Column(db.Integer)

    created = db.Column(db.Date, default=datetime.now)
    updated = db.Column(db.Date, onupdate=datetime.now)

    def __repr__(self):
        return "<Source(name='%s', version='%s', hashkey='%s')>" % (self.name, self.version, self.hashkey)

class TimePoint(db.Model):
    __tablename__ = 'timepoints'
    __table_args__ = (db.Index('unique_hash_time', "plugin_id", "metric_id", "user_id", "hashkey"), db.UniqueConstraint('hashkey'), )

    hash_vals = ["plugin_id", "metric_id", "user_id", "data"]

    id = db.Column(db.Integer, primary_key=True)
    plugin_id = db.Column(db.String(STRING_MAX), db.ForeignKey('plugins.hashkey'))
    metric_id = db.Column(db.String(STRING_MAX), db.ForeignKey('metrics.name'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    source_id = db.Column(db.String(STRING_MAX), db.ForeignKey("sources.name"))
    date = db.Column(db.Date)

    data = db.Column(db.Float)
    hashkey = db.Column(db.String(STRING_MAX))

    created = db.Column(db.Date, default=datetime.now)
    modified = db.Column(db.Date, onupdate=datetime.now)

    user = db.relationship("User", backref=db.backref('timepoints', order_by=id))
    plugin = db.relationship("Plugin", backref=db.backref('timepoints', order_by=id))
    metric = db.relationship("Metric", backref=db.backref('timepoints', order_by=id))
    source = db.relationship("Source", backref=db.backref('timepoints', order_by=id))

    def __repr__(self):
        return "<TimeSeries(plugin='%s', metric='%s', data='%s')>" % (self.plugin_id, self.metric_id, self.data)

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


"""
#Comment this out for now to avoid having to change both models.
class Blob(Base):
    __tablename__ = 'blob'
    __table_args__ = (Index('unique_hash_blob', "name", "user_id", "hashkey"), )

    hash_vals = ["plugin_id", "data", "user_id"]

    id = Column(Integer, primary_key=True)
    plugin_id = Column(String, ForeignKey('plugin.hashkey'))
    hashkey = Column(String)
    data = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", backref=backref('blobs', order_by=id))
    plugin = relationship("Plugin", backref=backref('blobs', order_by=id))

    def __repr__(self):
        return "<Blob(plugin='%s', metric='%s', data='%s')>" % (self.plugin_id, self.metric, self.data)

event.listen(Blob, 'before_insert', add_hashkey)
"""
