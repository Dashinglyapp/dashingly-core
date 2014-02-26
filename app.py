from flask import Flask
from core.web.main_views import main_views
from core.web.plugin_views import plugin_views
from core.database.models import db, User, Role
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.babel import Babel
from realize import settings
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.register_blueprint(main_views)
    app.register_blueprint(plugin_views)
    app.config.from_object('realize.settings')
    db.app = app
    db.init_app(app)
    return app

def create_test_app():
    app = create_app()
    app.config.from_object('realize.test_settings')
    return app

app = create_app()

babel = Babel(app)
celery = make_celery(app)

if __name__ == '__main__':
    db.create_all(app=create_app())
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    app.run(debug=settings.DEBUG)