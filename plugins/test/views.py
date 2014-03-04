from wtforms import IntegerField, TextField
from core.plugins.lib.forms import FormWidget, SettingsFormWidget
from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.views import WidgetView, ModelChartWidget
from plugins.test.models import SettingsModel, MoodModel, DataModel


class MoodForm(FormWidget):
    name = "mood"
    description = "Please enter some information about your mood."
    model = MoodModel
    metric_proxy = MetricProxy(name="mood")
    source_proxy = SourceProxy(name="self")

    data = IntegerField(description="Number on a 1-10 scale.")

class SurveyForm(FormWidget):
    name = "survey"
    description = "Please enter some long information about your mood."
    model = DataModel
    metric_proxy = MetricProxy(name="data")
    source_proxy = SourceProxy(name="self")

    text = TextField(description="Enter the mood you are feeling.")
    number = IntegerField(description="Number on a 1-10 scale.")

class SettingsForm(SettingsFormWidget):
    name = "settings"
    description = "Some settings for you."
    model = SettingsModel
    your_name = TextField(description="Enter your name, man!")

class DailyMoodChart(ModelChartWidget):
    name = 'daily_mood'
    description = 'Your mood every day.'
    model = MoodModel
    y_data_field = 'data'
    x_data_field = 'date'
    y_label = 'Mood'
    x_label = 'Date'
    x_name = 'Date'
    y_name = 'Mood'

class GetStuffView(WidgetView):
    name = "get_stuff"
    description = "Get stuff.  Duh."
    children = [MoodForm, SurveyForm, DailyMoodChart]