class MetricManager(object):
    def __init__(self, user):
        self.user = user

    def list(self):
        return self.user.metrics

    def list_with_values(self, start, end):
        metrics = self.list()


    def lookup_metric(self, plugin_proxy, metric_proxy, start=None, end=None):
        from core.plugins.manager import PluginManager
        manager = PluginManager(self.user)
        context, wrapper = manager.get_context_and_wrapper(plugin_proxy.hashkey)

        return wrapper.query_time_range("date",
                                        plugin_proxy=plugin_proxy,
                                        metric_proxy=metric_proxy,
                                        start=start,
                                        end=end
        )