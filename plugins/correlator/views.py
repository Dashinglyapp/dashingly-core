from core.plugins.lib.fields import DataTypes
from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import ChartView, LineDescriptor, DailyCountChartView
from plugins.correlator.models import Correlations, DirectionChanges
from plugins.ehr.models import EHRData
from plugins.github.models import GithubCommits
import os

class CorrelationView(View):
    model = Correlations
    description = "Correlations"
    tags = ["correlations", "view"]
    name = "correlations"


    def get(self, data):
        start = data.get('start', None)
        end = data.get('end', None)
        models = self.manager.query_class_range('date', self.model, start=start, end=end)

        data = []
        for m in models:
            data.append({
                'series1': m.series1,
                'message': m.message
            })

            if hasattr(m, "series2"):
                data['series2'] = m.series2

        return {
            'data': data,
            'description': self.description
        }

class DirectionView(CorrelationView):
    name = "directions"
    description = "Trends"
    model = DirectionChanges
    tags = ["correlations", "view"]
