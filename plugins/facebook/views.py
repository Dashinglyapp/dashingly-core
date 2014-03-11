from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import DailyCountChartView
from plugins.facebook.models import NewsFeed

class DailyActivityChart(DailyCountChartView):
    name = 'daily_activity'
    description = 'How much activity you have per day on facebook.'
    y_label = 'Activity'
    model = NewsFeed
    x_label = 'Date'
    x_name = 'Date'
    y_name = 'Daily activity'
    x_data_field = 'date'

class FacebookView(View):
    name = "facebook_view"
    description = "View for facebook."
    children = [DailyActivityChart]