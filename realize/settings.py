from path import path
from datetime import timedelta
import os

DB_URL = 'sqlite:///realize.db'
DEBUG = True

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH.dirname()
ENV_ROOT = REPO_PATH.dirname()

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
    },
    'facebook': {
        'request_token_params': {'scope': 'email, user_birthday, basic_info, user_likes, user_relationships, user_status, read_stream, read_mailbox, user_online_presence, user_actions.music, user_actions.news, user_actions.video, user_games_activity'},
        'base_url': 'https://graph.facebook.com/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://graph.facebook.com/oauth/access_token',
        'authorize_url': 'https://graph.facebook.com/oauth/authorize'
    },
    'fitbit': {
        'request_token_params': {'scope': ''},
        'base_url': 'http://api.fitbit.com/',
        'request_token_url': 'http://api.fitbit.com/oauth/request_token',
        'access_token_method': 'POST',
        'access_token_url': 'http://api.fitbit.com/oauth/access_token',
        'authorize_url': 'http://www.fitbit.com/oauth/authorize'
    }
}

MAX_TOKEN_AGE = 7 * 24 * 60 * 60 # seconds
OAUTH_MAX_TOKEN_AGE = 5 * 60 # seconds
VIEW_HASHKEY_LENGTH = 20

RESOURCE_DATA_VERSION = 1
API_VERSION = ".1"
API_SPEC_URL = "/api/v1/spec"

DEFAULT_TIMEZONE = "UTC"

WTF_CSRF_ENABLED = False
ADMIN_NAME = "Realize Admin"

try:
    from realize.private import *
except:
    pass