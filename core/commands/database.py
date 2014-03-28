from flask.ext.script import Command
from alembic.config import Config
from alembic import command
from flask.ext.script import Option
from sqlalchemy.exc import IntegrityError
from flask import current_app
import os
from app import db
from core.database.models import Role, User
from flask.ext.security import SQLAlchemyUserDatastore

alembic_cfg = Config(os.path.join(current_app.config['REPO_PATH'], "alembic.ini"))

class UpgradeDB(Command):
    def run(self):
        command.upgrade(alembic_cfg, "head")
        roles = ['admin', 'user', 'superuser']

        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        for r in roles:
            user_datastore.find_or_create_role(r)
        try:
            db.session.commit()
        except IntegrityError:
            # Happens if records already exist.
            db.session.rollback()

class MakeAdmin(Command):
    option_list = (
        Option('--user', '-u', dest='user', help="User email address."),
    )
    def run(self, user):
        from app import db
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        u = User.query.filter_by(email=user).first()
        role = user_datastore.find_or_create_role('admin')
        user_datastore.add_role_to_user(u, role)
        db.session.commit()
