from settings import *

DB_URL = "sqlite:///test.db"
SQLALCHEMY_DATABASE_URI = DB_URL
TESTING = True

SECRET_KEY = "test"
SECURITY_PASSWORD_HASH = "plaintext"
SECURITY_PASSWORD_SALT = None
