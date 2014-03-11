from wtforms import IntegerField, TextField, SelectField
from wtforms.validators import required
from core.plugins.lib.views.forms import FormView, SettingsFormView
from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import ModelChartView
from plugins.test.models import SettingsModel, MoodModel, DataModel


class MoodForm(FormView):
    name = "mood"
    description = "Please enter some information about your mood."
    model = MoodModel
    metric_proxy = MetricProxy(name="mood")
    source_proxy = SourceProxy(name="self")

    data = IntegerField('Mood', [required()], description="Number on a 1-10 scale.")

class SurveyForm(FormView):
    name = "survey"
    description = "Please enter some long information about your mood."
    model = DataModel
    metric_proxy = MetricProxy(name="data")
    source_proxy = SourceProxy(name="self")

    text = TextField(description="Enter the mood you are feeling.")
    number = IntegerField(description="Number on a 1-10 scale.")

class SettingsForm(SettingsFormView):
    name = "settings"
    description = "Some settings for you."
    model = SettingsModel
    your_name = TextField(description="Enter your name, man!")

class DailyMoodChart(ModelChartView):
    name = 'daily_mood'
    description = 'Your mood every day.'
    model = MoodModel
    y_data_field = 'data'
    x_data_field = 'date'
    y_label = 'Mood'
    x_label = 'Date'
    x_name = 'Date'
    y_name = 'Mood'