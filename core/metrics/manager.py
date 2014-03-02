import calendar
from core.manager import BaseManager, ExecutionContext

class MetricManager(BaseManager):
    def list(self):
        return self.user.metrics

    def list_with_values(self, start=None, end=None):
        from core.plugins.lib.proxies import PluginProxy, MetricProxy
        plugins = self.user.plugins

        metrics = {}
        for plugin in plugins:
            models = plugin.pluginmodels
            for model in models:
                vals = self.lookup_metric(PluginProxy(hashkey=plugin.hashkey, name=plugin.name), MetricProxy(name=model.metric.name), start=start, end=end)
                metrics[model.metric.name] = {
                    'y': [val.data for val in vals],
                    'x': [calendar.timegm(val.date.utctimetuple()) for val in vals],
                    'metric': model.metric
                }
        return metrics

    def lookup_metric(self, plugin_proxy, metric_proxy, start=None, end=None):
        from core.plugins.manager import PluginManager
        context = ExecutionContext(user=self.user, plugin=plugin_proxy)
        manager = PluginManager(context)
        manager = manager.get_manager(plugin_proxy.hashkey)
        return manager.query_time_range("date",
                                        plugin_proxy=plugin_proxy,
                                        metric_proxy=metric_proxy,
                                        start=start,
                                        end=end
        )