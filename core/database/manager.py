from models import Metric, Source, Plugin, TimePoint, Blob, PluginModel
from core.plugins.proxies import MetricProxy, SourceProxy, PluginProxy, PluginModelProxy
from core.util import InvalidObjectException, get_cls
from core.database.permissions import PermissionsManager
from core.manager import BaseManager
from sqlalchemy.exc import IntegrityError
from core.plugins.models import DuplicateRecord
from realize.log import logging

log = logging.getLogger(__name__)

class DBManager(BaseManager):
    id_vals = ["id", "hashkey"]
    modify_vals = ["date"]
    get_vals = ["created", "modified"]
    vals = id_vals + modify_vals + get_vals

    def __init__(self, context, session=None):
        super(DBManager, self).__init__(context)
        self.session = session

        if self.plugin is not None:
            self.perm_manager = PermissionsManager(self.context)

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
        source = get_cls(self.session, Source, obj.source_proxy)

        attribs = {
            'source': source,
            'metric': metric,
            'data': data,
            'plugin': self.plugin,
            'plugin_model_id': obj.hashkey,
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

        try:
            self.session.add(mod)
            self.session.commit()
        except IntegrityError:
            log.exception("Found a duplicate record.")
            self.session.rollback()
            raise DuplicateRecord()

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
        self.session.commit()

    def delete(self, obj):
        mod = self.find_model(obj, id=obj.id)
        if self.perm_manager.check_perms(mod, "delete"):
            self.session.delete(mod)
        return obj

    def update(self, obj):
        mod = self.find_model(obj, id=obj.id)
        if self.perm_manager.check_perms(mod, "update"):
            for v in self.modify_vals:
                setattr(mod, v, getattr(obj, v))
            mod.data = obj.get_data()
        return obj

    def _query_base(self, plugin_proxy=None, metric_proxy=None, query_cls=TimePoint):
        query = self.session.query(query_cls).order_by("date")
        if self.user is not None:
            query = query.filter(getattr(query_cls, "user") == self.user)
        elif self.group is not None:
            query = query.filter(getattr(query_cls, "group") == self.group)

        query = query.order_by(query_cls.date.asc())
        if plugin_proxy is not None:
            plugin = get_cls(self.session, Plugin, plugin_proxy)
            query = query.filter(getattr(query_cls, "plugin") == plugin)

        if metric_proxy is not None:
            metric = get_cls(self.session, Metric, metric_proxy)
            query = query.filter(getattr(query_cls, "metric") == metric)

        return query

    def lookup_plugin_model(self, obj):
        from core.plugins.loader import plugins
        model_key = obj.plugin_model.hashkey
        plugin_key = obj.plugin.hashkey
        plugin = plugins[plugin_key]
        for m in plugin.models:
            if m.hashkey == model_key:
                return m
        return None

    def translate_object(self, obj):
        has_perm = self.perm_manager.check_perms(obj, "view")
        if not has_perm:
            return None

        tp = self.lookup_plugin_model(obj)()
        tp.metric_proxy = MetricProxy(name=obj.metric.name)
        tp.plugin_proxy = PluginProxy(name=obj.plugin.name, hashkey=obj.plugin.hashkey)
        tp.source_proxy = SourceProxy(name=obj.source.name)

        for v in self.vals:
            setattr(tp, v, getattr(obj, v))
        tp.set_data(obj.data)

        return tp

    def translate_objects(self, query):
        tps = []
        for obj in query:
            translation = self.translate_object(obj)
            if translation is not None:
                tps.append(translation)
        return tps

    def query_range(self, query_column, model_cls, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        query = self._query_base(plugin_proxy, metric_proxy, query_cls=model_cls)
        if start is not None:
            query = query.filter(getattr(model_cls, query_column) >= start)
        if end is not None:
            query = query.filter(getattr(model_cls, query_column) <= end)

        return self.translate_objects(query.all())

    def query_filter(self, model_cls, plugin_proxy=None, metric_proxy=None, first=False, last=False, **kwargs):
        query = self._query_base(plugin_proxy, metric_proxy, query_cls=model_cls)
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

    def query_time_range(self, query_column, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        return self.query_range(query_column, TimePoint, plugin_proxy, metric_proxy, start, end)

    def query_time_filter(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(TimePoint, plugin_proxy, metric_proxy, **kwargs)

    def query_blob_range(self, query_column, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        return self.query_range(query_column, Blob, plugin_proxy, metric_proxy, start, end)

    def query_blob_filter(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(Blob, plugin_proxy, metric_proxy, **kwargs)

    def query_blob_last(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(Blob, plugin_proxy, metric_proxy, last=True, **kwargs)

    def query_blob_first(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(Blob, plugin_proxy, metric_proxy, first=True, **kwargs)

    def query_time_last(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(TimePoint, plugin_proxy, metric_proxy, last=True, **kwargs)

    def query_time_first(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(TimePoint, plugin_proxy, metric_proxy, first=True, **kwargs)

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

        model.hashkey = val.hashkey

