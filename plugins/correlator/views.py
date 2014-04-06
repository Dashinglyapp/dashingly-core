from core.plugins.lib.fields import DataTypes
from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import ChartView, LineDescriptor, DailyCountChartView
from plugins.correlator.models import Correlations
from plugins.ehr.models import EHRData
from plugins.github.models import GithubCommits
import os

class CorrelationView(View):
    model = Correlations
    tags = ["correlation", "view"]


    def get(self, data):
        start = data.get('start', None)
        end = data.get('end', None)
        models = self.manager.query_class_range(self.model, start=start, end=end)

        data = []
        for m in models:
            data.append({
                'series1': m.series1,
                'series2': m.series2,
                'message': m.message
            })

        return {
            'data': data
        }