from models import Metric, Source, Plugin, PluginData, PluginModel
from core.plugins.lib.proxies import MetricProxy, SourceProxy, PluginProxy, PluginModelProxy
from core.util import InvalidObjectException, get_cls
from core.database.permissions import DatabasePermissionsManager
from core.manager import BaseManager
from sqlalchemy.exc import IntegrityError
from core.plugins.lib.models import DuplicateRecord
from realize.log import logging

log = logging.getLogger(__name__)

class DatabaseManager(BaseManager):
    id_vals = ["id", "hashkey"]
    modify_vals = ["date"]
    get_vals = ["created", "updated"]
    vals = id_vals + modify_vals + get_vals

    def __init__(self, context, session=None):
        super(DatabaseManager, self).__init__(context)
        self.session = session

        if self.plugin is not None:
            self.perm_manager = DatabasePermissionsManager(self.context)

    def get_or_create(self, obj, query_data=False):
        new_obj = self.get(obj, query_data=query_data)
        if new_obj is None:
            new_obj = self.add(obj)
        else:
            new_obj = self.translate_object(new_obj)
        return new_obj

    def setup_model(self, obj):
        data = obj.get_data()

        metric = get_cls(self.session, Metric, obj.metric_proxy)
        source = get_cls(self.session, Source, obj.source_proxy, create=True)

        attribs = {
            'source': source,
            'metric': metric,
            'data': data,
            'plugin': self.plugin,
            'plugin_model_id': obj.plugin_model_proxy.hashkey,
            }

        if self.user is not None:
            attribs['user'] = self.user
        elif self.group is not None:
            attribs['group'] = self.group

        for v in self.modify_vals:
            attribs[v] = getattr(obj, v)

        return attribs

    def get(self, obj, query_data=False):
        attribs = self.setup_model(obj)
        if not query_data:
            del attribs['data']
        instance = self.session.query(obj.model_cls).filter_by(**attribs).first()
        return instance

    def add(self, obj):
        attribs = self.setup_model(obj)
        mod = obj.model_cls(**attribs)

        self.session.add(mod)
        self.commit()

        obj.id = mod.id
        obj.hashkey = mod.hashkey

        return obj

    def find_model(self, obj, **kwargs):
        q = self.session.query(obj.model_cls)
        for attr, value in kwargs.items():
            q = q.filter(getattr(obj.model_cls, attr) == value)
        if q.count() > 0:
            return q.first()
        else:
            raise InvalidObjectException()

    def commit(self):
        try:
            self.session.commit()
        except IntegrityError:
            log.exception("Found a duplicate record.")
            self.session.rollback()
            raise DuplicateRecord()

    def delete(self, obj):
        mod = self.find_model(obj, id=obj.id)
        if self.perm_manager.check_perms(mod, "delete"):
            self.session.delete(mod)
            self.commit()
        return obj

    def update(self, obj):
        mod = self.find_model(obj, id=obj.id)
        if self.perm_manager.check_perms(mod, "update"):
            for v in self.modify_vals:
                setattr(mod, v, getattr(obj, v))
            mod.data = obj.get_data()
            self.commit()
        return obj

    def query_models(self, plugin_proxy=None, metric_proxy=None, query_cls=PluginData):
        models = self.session.query(PluginModel).order_by("date")
        if plugin_proxy is not None:
            plugin = get_cls(self.session, Plugin, plugin_proxy, attrs=["hashkey"])
            models = models.filter(getattr(query_cls, "plugin") == plugin)

        if metric_proxy is not None:
            metric = get_cls(self.session, Metric, metric_proxy)
            models = models.filter(getattr(query_cls, "metric") == metric)
        return models.distinct()

    def _query_base(self, plugin_proxy=None, metric_proxy=None, query_cls=PluginData, plugin_model_proxy=None):
        query = self.session.query(query_cls).order_by("date")
        if self.user is not None:
            query = query.filter(getattr(query_cls, "user") == self.user)

        query = query.order_by(query_cls.date.asc())
        if plugin_proxy is not None:
            plugin = get_cls(self.session, Plugin, plugin_proxy, attrs=["hashkey"])
            query = query.filter(getattr(query_cls, "plugin") == plugin)

        if metric_proxy is not None:
            metric = get_cls(self.session, Metric, metric_proxy)
            query = query.filter(getattr(query_cls, "metric") == metric)

        if plugin_model_proxy is not None:
            plugin_model = get_cls(self.session, PluginModel, plugin_model_proxy, attrs=["hashkey"])
            query = query.filter(getattr(query_cls, "plugin_model") == plugin_model)

        return query

    def lookup_plugin_model(self, obj):
        from core.plugins.loader import plugins
        model_key = obj.plugin_model.hashkey
        plugin_key = obj.plugin.hashkey
        plugin = plugins[plugin_key]
        for m in plugin.models:
            if m.plugin_model_proxy.hashkey == model_key:
                return m
        return None

    def translate_object(self, obj):
        has_perm = self.perm_manager.check_perms(obj, "view")
        if not has_perm:
            log.info("Incorrect permissions.")
            return None

        tp = self.lookup_plugin_model(obj)()
        tp.metric_proxy = MetricProxy(name=obj.metric.name)
        tp.plugin_proxy = PluginProxy(name=obj.plugin.name, hashkey=obj.plugin.hashkey)
        tp.source_proxy = SourceProxy(name=obj.source.name)

        for v in self.vals:
            setattr(tp, v, getattr(obj, v))
        tp.set_data(obj.data)
        if obj.user is not None:
            tp.user = obj.user.email

        return tp

    def translate_objects(self, query):
        tps = []
        for obj in query:
            translation = self.translate_object(obj)
            if translation is not None:
                tps.append(translation)
        return tps

    def _query_range(self, query_column, model_cls, plugin_proxy=None, metric_proxy=None, start=None, end=None, plugin_model_proxy=None):
        query = self._query_base(plugin_proxy, metric_proxy, query_cls=model_cls, plugin_model_proxy=plugin_model_proxy)
        if start is not None:
            query = query.filter(getattr(model_cls, query_column) >= start)
        if end is not None:
            query = query.filter(getattr(model_cls, query_column) <= end)

        return self.translate_objects(query.all())

    def _query_filter(self, model_cls, plugin_proxy=None, metric_proxy=None, plugin_model_proxy=None, first=False, last=False, **kwargs):
        query = self._query_base(plugin_proxy, metric_proxy, query_cls=model_cls, plugin_model_proxy=plugin_model_proxy)
        for attr, value in kwargs.items():
            query = query.filter(getattr(model_cls, attr) == value)

        if first or last:
            if first:
                if query.count() > 0:
                    query = query.first()
                else:
                    return None
            if last:
                if query.count() > 0:
                    query = query[-1]
                else:
                    return None
            return self.translate_object(query)

        return self.translate_objects(query.all())

    def query_range(self, query_column, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        return self._query_range(query_column, PluginData, plugin_proxy, metric_proxy, start, end)

    def query_filter(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self._query_filter(PluginData, plugin_proxy, metric_proxy, **kwargs)

    def query_last(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self._query_filter(PluginData, plugin_proxy, metric_proxy, last=True, **kwargs)

    def query_first(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self._query_filter(PluginData, plugin_proxy, metric_proxy, first=True, **kwargs)

    def get_query_class(self, obj):
        from core.plugins.lib.models import PluginDataModel
        if issubclass(obj, PluginDataModel):
            query_cls = PluginData
        else:
            raise InvalidObjectException()
        return query_cls

    def query_class_filter(self, cls, **kwargs):
        query_cls = self.get_query_class(cls)
        return self._query_filter(query_cls, plugin_model_proxy=cls.plugin_model_proxy, **kwargs)

    def query_class_range(self, query_column, cls, start=None, end=None):
        query_cls = self.get_query_class(cls)
        return self._query_range(query_column, query_cls, plugin_model_proxy=cls.plugin_model_proxy, start=start, end=end)

    def register_plugin(self, plugin_cls):
        plugin_proxy = PluginProxy(name=plugin_cls.name, hashkey=plugin_cls.hashkey)
        plugin = get_cls(self.session, Plugin, plugin_proxy, attrs=["name", "hashkey"], create=True)
        if plugin_cls.models is not None:
            for m in plugin_cls.models:
                get_cls(self.session, Metric, m.metric_proxy, create=True)
                get_cls(self.session, Source, m.source_proxy, create=True)
                self.register_model(plugin_cls, m)
        return plugin

    def register_model(self, plugin_cls, model):
        proxy = PluginModelProxy(
            plugin_id=plugin_cls.hashkey,
            metric_id=model.metric_proxy.name,
            name=model.__name__
        )
        val = get_cls(self.session, PluginModel, proxy, attrs=["name", "plugin_id", "metric_id"], create=True)

        proxy.hashkey = val.hashkey
        model.plugin_model_proxy = proxy

