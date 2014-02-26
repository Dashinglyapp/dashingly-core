from path import path
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