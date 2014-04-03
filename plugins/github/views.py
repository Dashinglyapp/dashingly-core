from core.plugins.lib.fields import DataTypes
from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import ChartView, LineDescriptor, DailyCountChartView
from plugins.github.models import GithubCommits

class DailyCommitChart(DailyCountChartView):
    name = 'daily_commits'
    description = 'How many commits you made in github per day.'
    model = GithubCommits
    y_data_field = 'data'
    x_data_field = 'date'
    y_label = 'Commit count'
    x_label = 'Date'
    x_name = 'Date'
    y_name = 'Daily commits'
    aggregation_method = "count"