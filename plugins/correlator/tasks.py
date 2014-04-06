import csv
import random
from core.manager import ExecutionContext
from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.tasks import TaskBase, Interval
from core.plugins.lib.proxies import TaskProxy, PluginProxy
from datetime import datetime, timedelta
from plugins.correlator.models import Correlations, DirectionChanges
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
from datetime import datetime

DATA_PATH = os.path.abspath(os.path.join(current_app.config['REPO_PATH'], "plugins", "ehr", "data"))

class CorrTaskBase(TaskBase):
    def make_ts(self, v):
        x = v['data']['x']['data']
        new_x = []
        for tp in x:
            new_x.append(parser.parse(tp))
        y = v['data']['y'][0]['data']
        new_y = []
        for tp in y:
            new_y.append(float(tp))
        ts = Series(new_y, index=new_x)
        ts = ts.asfreq('D', method='pad')
        return ts

    def get_view_data(self):
        list = ScopeViewsList()
        data = list.get("user", self.manager.user.hashkey)
        views = []
        for view in data:
            if 'daily-count-timeseries' in view['tags']:
                views.append(view)
        view_data = []
        for v in views:
            context = ExecutionContext(user=self.manager.user, plugin=PluginProxy(hashkey=v['plugin'], name=""))
            manager = ViewManager(context, manager=self.manager)
            view_d = manager.handle_route(v['hashkey'], "get", {}, v['hashkey'])
            view_data.append(json.loads(view_d.data))
        return view_data

class SetupTask(TaskBase):
    task_proxy = TaskProxy(name="setup")

    def run(self):
        corr = CorrelationTask(context=self.context, manager=self.manager)
        corr.run()

        dir = DirectionTask(context=self.context, manager=self.manager)
        dir.run()

class CorrelationTask(CorrTaskBase):
    task_proxy = TaskProxy(name="correlate")

    def run(self):
        correlations = []
        view_data = self.get_view_data()
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
                        series1=v['hashkey'],
                        series2=v2['hashkey'],
                        message="{0} is associated with {1} at a level of {2}".format(v['description'], v2['description'], corr)
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

class DirectionTask(CorrTaskBase):
    task_proxy = TaskProxy(name="direction")

    def run(self):
        view_data = self.get_view_data()
        lookback_periods = [365, 30, 7]
        now = datetime.now()
        messages = []
        for (i, v) in enumerate(view_data):
            ts = self.make_ts(v)
            if len(ts.index) < 3:
                continue
            start = ts.index[0]
            end = ts.index[-1]

            for l in lookback_periods:
                mid = now - timedelta(days=l)

                slice1 = ts[start:mid].mean()
                slice2 = ts[mid:end].mean()

                ratio = slice2/slice1

                if np.isnan(ratio):
                    continue

                message_middle = ""

                if ratio > 2:
                    message_middle = "increased significantly"
                elif ratio > 1:
                    message_middle = "increased"
                elif ratio < .5:
                    message_middle = "decreased significantly"
                elif ratio < 1:
                    message_middle = "decreased"

                messages.append(dict(
                    series1=v['hashkey'],
                    message="{0} has {1} in the past {2} days".format(v['description'], message_middle, l)
                ))
        for m in messages:
            obj = DirectionChanges(
                series1=m['series1'],
                message=m['message']
            )
            try:
                self.manager.add(obj)
            except DuplicateRecord:
                pass











