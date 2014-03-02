from core.plugins.lib.views import WidgetView, ModelChartWidget
from plugins.github.models import DailyCommits

class GithubWidgetView(WidgetView):
    path = "charts"
    widgets = {
        'chart': ModelChartWidget(
            'daily_commits',
            'How many commits you made in github per day.',
            model=DailyCommits,
            y_data_field='data',
            x_data_field='date',
            y_label='Commit count',
            x_label='Date',
            x_name='Date',
            y_name='Daily commits'
        )
    }