from flask import Flask, jsonify
from flask_security.utils import md5
from core.database.models import db, User, Role
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.babel import Babel
from realize import settings
from celery import Celery
from flask_oauthlib.client import OAuth
from flask_wtf.csrf import CsrfProtect
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from flask.ext import restful

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

def make_json_error(ex):
    code = (ex.code
            if isinstance(ex, HTTPException)
            else 500)
    response = jsonify(message=str(ex), error=True, code=code)
    response.status_code = code
    return response

def register_blueprints(app):
    from core.web.main_views import main_views
    from core.web.plugin_views import plugin_views
    from core.oauth.oauth_views import oauth_views
    from core.web.resource_views import resource_views
    from core.web.user_views import user_views
    from core.web.group_views import group_views
    from core.tasks.task_views import task_views
    from core.web.auth_views import auth_views

    blueprints = [main_views, plugin_views, oauth_views, resource_views, user_views, group_views, task_views, auth_views]
    for bp in blueprints:
        app.register_blueprint(bp)
        bp.config = app.config

def register_extensions(app):
    oauth.init_app(app)
    babel.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object('realize.settings')

    db.app = app
    db.init_app(app)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

def create_test_app():
    app = create_app()
    app.config.from_object('realize.test_settings')

    db.app = app
    db.init_app(app)
    register_blueprints(app)
    register_extensions(app)

    return app

def token_loader(token, max_age=settings.MAX_TOKEN_AGE):
    """
    Used to patch flask-security to expire tokens after a time limit.
    """
    from flask_security.core import AnonymousUser
    try:
        data = app.extensions['security'].remember_token_serializer.loads(token, max_age=max_age)
        user = app.extensions['security'].datastore.find_user(id=data[0])
        if user and md5(user.password) == data[1]:
            return user
    except Exception:
        pass
    return AnonymousUser()


app = create_app()
api = restful.Api()
oauth = OAuth()
babel = Babel()
celery = make_celery(app)

if __name__ == '__main__':
    register_blueprints(app)
    register_extensions(app)
    api.init_app(app)
    db.create_all(app=app)

    # Patch flask security to expire tokens after a time limit.
    app.extensions['security'].login_manager.token_loader(token_loader)

    app.run(debug=settings.DEBUG, host="0.0.0.0")