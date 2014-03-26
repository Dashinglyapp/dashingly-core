from settings import *
import json

DEBUG = False

with open(ENV_ROOT / "env.json") as env_file:
    ENV_TOKENS = json.load(env_file)

with open(ENV_ROOT / "auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)

DB_URL = AUTH_TOKENS.get("DB_URL", DB_URL)
SQLALCHEMY_DATABASE_URI = DB_URL

SECRET_KEY = AUTH_TOKENS.get("SECRET_KEY", SECRET_KEY)
SECURITY_PASSWORD_SALT = AUTH_TOKENS.get("SECURITY_PASSWORD_SALT", SECURITY_PASSWORD_SALT)

OAUTH_SECRETS = AUTH_TOKENS.get("OAUTH_SECRETS", {})