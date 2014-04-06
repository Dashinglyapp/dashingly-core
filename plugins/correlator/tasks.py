import csv
import random
from core.manager import ExecutionContext
from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.tasks import TaskBase, Interval
from core.plugins.lib.proxies import TaskProxy, PluginProxy
from datetime import datetime, timedelta
from plugins.correlator.models import Correlations
from plugins.ehr.models import EHRData
from plugins.github.models import GithubCommits
from core.plugins.lib.proxies import MetricProxy
from plugins.github import manifest
import pytz
from flask import current_app
from core.views.manager import ViewManager
from core.web.plugin_views import ScopeViewsList, PluginViewsDetail
import os
import json
from pandas import Series
import numpy as np
import calendar
from dateutil import parser

DATA_PATH = os.path.abspath(os.path.join(current_app.config['REPO_PATH'], "plugins", "ehr", "data"))

class CorrelationTask(TaskBase):
    task_proxy = TaskProxy(name="correlate")

    def make_ts(self, v):
        x = v['data']['x']['data']
        new_x = []
        for tp in x:
            new_x.append(parser.parse(tp).timetuple())
        y = v['data']['y'][0]['data']
        new_y = []
        for tp in y:
            new_y.append(float(tp))
        ts = Series(new_y, index=new_x)
        return ts

    def run(self):
        list = ScopeViewsList()
        data = list.get("user", self.manager.user.hashkey)
        views = []
        for view in data:
            if 'daily-count-timeseries' in view['tags']:
                views.append(view)
        view_data = []
        correlations = []
        for v in views:
            context = ExecutionContext(user=self.manager.user, plugin=PluginProxy(hashkey=v['plugin'], name=""))
            manager = ViewManager(context, manager=self.manager)
            view_d = manager.handle_route(v['hashkey'], "get", {}, v['hashkey'])
            view_data.append(json.loads(view_d.data))
        for (i, v) in enumerate(view_data):
            ts = self.make_ts(v)

            for (j, v2) in enumerate(view_data):
                ts2 = self.make_ts(v2)
                if i == j:
                    continue
                ts = ts.reindex(ts2.index, method='ffill')
                corr = ts.corr(ts2)
                print corr
                if np.isnan(corr):
                    continue
                else:
                    correlations.append(dict(
                        series1=v.hashkey,
                        series2=v2.hashkey,
                        message="{0} is associated with {1} at a level of {2}".format(v.name, v2.name, corr)
                    ))
        for c in correlations:
            obj = Correlations(
                series1=c['series1'],
                series2=c['series2'],
                message=c['message']
            )
            try:
                self.manager.add(obj)
            except DuplicateRecord:
                pass






