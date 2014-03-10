from flask.ext.script import Command
from alembic.config import Config
from alembic import command
from sqlalchemy.exc import IntegrityError
from realize import settings
import os
from app import db
from core.database.models import Role

alembic_cfg = Config(os.path.join(settings.REPO_PATH, "alembic.ini"))

class UpgradeDB(Command):
    def run(self):
        command.upgrade(alembic_cfg, "head")
        roles = [
            Role(name='admin'),
            Role(name='user'),
            Role(name='superuser')
        ]

        for r in roles:
            db.session.add(r)
        try:
            db.session.commit()
        except IntegrityError:
            # Happens if records already exist.
            db.session.rollback()

class MakeAdmin(Command):
    pass
