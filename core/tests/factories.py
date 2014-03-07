from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from factory.alchemy import SQLAlchemyModelFactory
from core.tests.base import db
import factory
from datetime import datetime
from core.database.models import User, Plugin, Metric, Source, PluginData, PluginModel,  UserItem
from realize.log import logging

log = logging.getLogger(__name__)

class BaseFactory(SQLAlchemyModelFactory):
    FACTORY_SESSION = db.session

    @classmethod
    def _setup_next_sequence(cls, *args, **kwargs):
        """Compute the next available PK, based on the 'pk' database field."""
        session = cls.FACTORY_SESSION
        model = cls.FACTORY_FOR

        check_cls = model
        if model in [Plugin, Source, PluginModel, Metric]:
            check_cls = UserItem

        pk = getattr(check_cls, "id")
        pks = session.query(pk).all()

        if len(pks) > 0:
            max_pk = max(pks)[0]
        else:
            max_pk = None
        if isinstance(max_pk, int):
            return max_pk + 1 if max_pk else 1
        else:
            return 1

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        session = cls.FACTORY_SESSION
        obj = target_class(*args, **kwargs)
        session.add(obj)


        try:
            session.commit()
        except IntegrityError:
            log.exception("Integrity error on save.")
            session.rollback()
        except FlushError:
            log.exception("Flush error on save.")
            session.rollback()

        mod = session.query(target_class).filter(getattr(target_class, "id") == obj.id).first()
        if hasattr(mod, "hashkey"):
            obj.hashkey = mod.hashkey
        return obj

class UserFactory(BaseFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: u'User %d' % n)
    email = factory.Sequence(lambda n: u'Email %d' % n)
    password = "testtest"

    @factory.post_generation
    def plugins(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for plugin in extracted:
                self.plugins.append(plugin)


class UserItemFactory(BaseFactory):
    name = factory.Sequence(lambda n: u"Item %d" % n)

class PluginFactory(UserItemFactory):
    FACTORY_FOR = Plugin

    hashkey = factory.Sequence(lambda n: "Key %d" % n)

class MetricFactory(UserItemFactory):
    FACTORY_FOR = Metric

class SourceFactory(UserItemFactory):
    FACTORY_FOR = Source

class PluginModelFactory(UserItemFactory):
    FACTORY_FOR = PluginModel

class PluginDataFactory(BaseFactory):
    FACTORY_FOR = PluginData
    date = datetime.now()
    data = None

    source = factory.SubFactory(SourceFactory)
    metric = factory.SubFactory(MetricFactory)
    plugin_model = factory.SubFactory(PluginModelFactory)
