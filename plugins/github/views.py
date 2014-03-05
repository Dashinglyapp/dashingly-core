from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import ModelChartView
from plugins.github.models import DailyCommits

class DailyCommitChart(ModelChartView):
    name = 'daily_commits'
    description = 'How many commits you made in github per day.'
    model = DailyCommits
    y_data_field = 'data'
    x_data_field = 'date'
    y_label = 'Commit count'
    x_label = 'Date'
    x_name = 'Date'
    y_name = 'Daily commits'

class GithubView(View):
    name = "github_view"
    description = "View for github."
    children = [DailyCommitChart]