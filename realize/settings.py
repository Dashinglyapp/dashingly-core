from path import path
from datetime import timedelta
import os

DB_URL = 'sqlite:///realize.db'
DEBUG = True
CACHE_TYPE = None

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH.dirname()
ENV_ROOT = REPO_PATH.dirname()


# ***** Which front-end should render the UI?
UI_REPO = os.path.join(REPO_PATH,"realize-ui-angular")
UI_DEV_PATH = os.path.join(UI_REPO, "build","app")
UI_PRODUCTION_PATH = os.path.join(UI_REPO, "dist", "app")
# Serve production if the production directory exists.  Otherwise serve dev.
TEMPLATES_PATH = UI_PRODUCTION_PATH
if os.path.exists(TEMPLATES_PATH) is False:
    # While developing, we serve the app directory
    TEMPLATES_PATH = UI_DEV_PATH
INDEX_TEMPLATE = "index.html"
OAUTH_TEMPLATE = "oauth.html"
# *****


PLUGIN_PATH = os.path.join(REPO_PATH, "plugins")

SECRET_KEY = "test"
USERNAME = "test"
EMAIL = "test@test.com"
PASSWORD = "test"

SQLALCHEMY_DATABASE_URI = DB_URL
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False

SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = "test"

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
BROKER_URL = 'redis://localhost:6379/2'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
CELERY_IMPORTS = ('core.tasks.runner',)

# toggles whether we're in dev or production mode
DEV_ENVIRON = True

CELERYBEAT_SCHEDULE = {
    'run-tasks-hourly': {
        'task': 'core.tasks.runner.run_interval_tasks',
        'schedule': timedelta(seconds=60 * 60),
        'args': (60 * 60, )
    },
    'run-tasks-daily': {
        'task': 'core.tasks.runner.run_interval_tasks',
        'schedule': timedelta(seconds=24 * 60 * 60),
        'args': (24 * 60 * 60, )
    }
    }

OAUTH_CONFIG = {
    'github': {
        'request_token_params': {'scope': 'user:email, repo'},
        'base_url': 'https://api.github.com/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'authorize_url': 'https://github.com/login/oauth/authorize'
    }
}

ADAM_UI_MIGRATION_JSON_INJECTION_TEST = {
    'VAR1': {
        'request_token_params': {'scope': 'user:email, repo'},
        'base_url': 'https://api.github.com/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'authorize_url': 'https://github.com/login/oauth/authorize'
    },
    'DEBUG':DEV_ENVIRON
}

try:
    from realize.private import *
except:
    pass