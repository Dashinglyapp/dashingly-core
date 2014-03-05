from flask import Flask, jsonify
from flask_security.utils import md5
from core.web.main_views import main_views
from core.web.plugin_views import plugin_views
from core.oauth.oauth_views import oauth_views
from core.web.widget_views import widget_views
from core.web.user_views import user_views
from core.database.models import db, User, Role
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.babel import Babel
from realize import settings
from celery import Celery
from flask_oauthlib.client import OAuth
from flask_wtf.csrf import CsrfProtect
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

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
    response = jsonify(message=str(ex))
    response.status_code = (ex.code
                            if isinstance(ex, HTTPException)
                            else 500)
    return response

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.register_blueprint(main_views)
    app.register_blueprint(plugin_views)
    app.register_blueprint(oauth_views)
    app.register_blueprint(widget_views)
    app.register_blueprint(user_views)
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
    except:
        pass
    return AnonymousUser()


app = create_app()
oauth = OAuth(app)
csrf = CsrfProtect(app)
babel = Babel(app)
celery = make_celery(app)

if __name__ == '__main__':
    db.create_all(app=app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Patch flask security to expire tokens after a time limit.
    app.extensions['security'].login_manager.token_loader(token_loader)

    app.run(debug=settings.DEBUG, host="0.0.0.0")