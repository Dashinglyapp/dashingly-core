from flask.ext.script import Command
from alembic.config import Config
from alembic import command
from flask.ext.script import Option
from sqlalchemy.exc import IntegrityError
from realize import settings
import os
from app import db, user_datastore
from core.database.models import Role, User

alembic_cfg = Config(os.path.join(settings.REPO_PATH, "alembic.ini"))

class UpgradeDB(Command):
    def run(self):
        command.upgrade(alembic_cfg, "head")
        roles = ['admin', 'user', 'superuser']

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
        u = User.query.filter_by(email=user).first()
        role = user_datastore.find_or_create_role('admin')
        user_datastore.add_role_to_user(u, role)
        db.session.commit()
