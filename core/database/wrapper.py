from models import Metric, Source, Plugin, TimePoint, Blob, PluginModel
from core.plugins.proxies import MetricProxy, SourceProxy, PluginProxy, PluginModelProxy
from core.util import InvalidObjectException, get_cls

class DBWrapper(object):
    id_vals = ["id", "hashkey"]
    modify_vals = ["date"]
    get_vals = ["created", "modified"]
    vals = id_vals + modify_vals + get_vals

    def __init__(self, session, context):
        self.session = session
        self.context = context

    def add(self, obj):
        data = obj.get_data()

        metric = get_cls(self.session, Metric, obj.metric_proxy)
        source = get_cls(self.session, Source, obj.source_proxy)

        attribs = {
            'source': source,
            'metric': metric,
            'data': data,
            'plugin': self.context.plugin,
            'user': self.context.user,
            'plugin_model_id': obj.hashkey,
        }


        mod = obj.model_cls(**attribs)
        for v in self.modify_vals:
            setattr(mod, v, getattr(obj, v))

        self.session.add(mod)
        self.session.commit()
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
        if mod.user == self.context.user:
            self.session.delete(mod)
        return obj

    def update(self, obj):
        mod = self.find_model(obj, id=obj.id)
        if mod.user == self.context.user:
            for v in self.modify_vals:
                setattr(mod, v, getattr(obj, v))
            mod.data = obj.get_data()
        return obj

    def _query_base(self, plugin_proxy=None, metric_proxy=None, query_cls=TimePoint):
        query = self.session.query(query_cls).filter(getattr(query_cls, "user") == self.context.user).order_by(query_cls.date.asc())
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
            tps.append(self.translate_object(obj))
        return tps

    def query_range(self, query_column, model_cls, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        query = self._query_base(plugin_proxy, metric_proxy, query_cls=model_cls)
        if start is not None:
            query = query.filter(getattr(model_cls, query_column) >= start)
        if end is not None:
            query = query.filter(getattr(model_cls, query_column) <= end)

        return self.translate_objects(query.all())

    def query_filter(self, model_cls, plugin_proxy=None, metric_proxy=None, **kwargs):
        query = self._query_base(plugin_proxy, metric_proxy, query_cls=model_cls)
        for attr, value in kwargs.items():
            query = query.filter(getattr(model_cls, attr) == value)
        return self.translate_objects(query.all())

    def query_time_range(self, query_column, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        return self.query_range(query_column, TimePoint, plugin_proxy, metric_proxy, start, end)

    def query_time_filter(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(TimePoint, plugin_proxy, metric_proxy, **kwargs)

    def query_blob_range(self, query_column, plugin_proxy=None, metric_proxy=None, start=None, end=None):
        return self.query_range(query_column, Blob, plugin_proxy, metric_proxy, start, end)

    def query_blob_filter(self, plugin_proxy=None, metric_proxy=None, **kwargs):
        return self.query_filter(Blob, plugin_proxy, metric_proxy, **kwargs)

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