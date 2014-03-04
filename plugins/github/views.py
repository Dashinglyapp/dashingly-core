from core.plugins.lib.views import WidgetView, ModelChartWidget
from plugins.github.models import DailyCommits

class DailyCommitChart(ModelChartWidget):
    name = 'daily_commits'
    description = 'How many commits you made in github per day.'
    model = DailyCommits
    y_data_field = 'data'
    x_data_field = 'date'
    y_label = 'Commit count'
    x_label = 'Date'
    x_name = 'Date'
    y_name = 'Daily commits'

class GithubWidgetView(WidgetView):
    name = "github_widget"
    description = "Widget for github."
    children = [DailyCommitChart]