from models import Metric, Source, Plugin, TimePoint
from core.plugins.proxies import MetricProxy, SourceProxy, PluginProxy, TimePointProxy
from core.util import InvalidObjectException, get_cls

class DBWrapper(object):
    id_vals = ["id", "hashkey"]
    modify_vals = ["data", "date"]
    get_vals = ["created", "modified"]
    vals = id_vals + modify_vals + get_vals

    def __init__(self, session, context):
        self.session = session
        self.context = context

    def add(self, obj):
        data = obj.data

        metric = get_cls(self.session, Metric, obj.metric_proxy)
        source = get_cls(self.session, Source, obj.source_proxy)

        attribs = {
            'source': source,
            'metric': metric,
            'data': data,
            'plugin': self.context.plugin,
            'user': self.context.user
        }

        mod = obj.model_cls(**attribs)
        self.session.add(mod)

        obj.id = mod.id
        obj.hashkey = mod.hashkey

        return obj

    def find_model(self, obj, **kwargs):
        q = self.context.session.query(obj.model_cls)
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
        self.session.delete(mod)
        return obj

    def update(self, obj):
        mod = self.find_model(obj, id=obj.id)
        for v in self.modify_vals:
            setattr(mod, v, getattr(obj, v))
        return obj

    def _query_base(self, plugin_proxy, metric_proxy):
        plugin = get_cls(self.session, Plugin, plugin_proxy)
        metric = get_cls(self.session, Metric, metric_proxy)

        return (self.session.query(TimePoint).
                filter(TimePoint.plugin == plugin).
                filter(TimePoint.metric == metric))

    def translate_object(self, obj):
        tp = TimePointProxy()
        tp.metric = MetricProxy(name=obj.metric.name)
        tp.plugin = PluginProxy(name=obj.plugin.name, hashkey=obj.plugin.hashkey)
        tp.source = SourceProxy(name=obj.source.name)

        for v in self.vals:
            setattr(tp, v, getattr(obj, v))
        return tp

    def translate_objects(self, query):
        tps = []
        for obj in query:
            tps.append(self.translate_object(obj))
        return tps

    def query_range(self, plugin_proxy, metric_proxy, query_column, start=None, end=None):
        query = self._query_base(plugin_proxy, metric_proxy)
        if start is not None:
            query = query.filter(getattr(TimePoint, query_column) >= start)
        if end is not None:
            query = query.filter(getattr(TimePoint, query_column) <= end)

        return self.translate_objects(query.all())

    def query_filter(self, plugin_proxy, metric_proxy, **kwargs):
        query = self._query_base(plugin_proxy, metric_proxy)
        for attr, value in kwargs.items():
            query = query.filter(getattr(TimePoint, attr) == value)

        return self.translate_objects(query.all())

    def register_plugin(self, plugin_cls):
        plugin_proxy = PluginProxy(name=plugin_cls.name, hashkey=plugin_cls.hashkey)
        plugin = get_cls(self.session, Plugin, plugin_proxy, attrs=["name", "hashkey"], create=True)
        if plugin_cls.models is not None:
            for m in plugin_cls.models:
                metric = get_cls(self.session, Metric, m.metric_proxy, create=True)
                source = get_cls(self.session, Source, m.source_proxy, create=True)
        return plugin
