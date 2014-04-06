from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import DailyCountChartView
from plugins.fitbit.models import StepModel, DistanceModel, TimeInBedModel, MinutesAsleepModel, WeightModel, SleepEfficiencyModel, ActivityCaloriesModel, SleepStartTimeModel, CaloriesInModel, CaloriesModel, WaterModel

class BaseFitbitView(DailyCountChartView):
    name = None
    model = None
    description = None
    y_label = None
    y_name = None
    y_data_field = 'value'
    x_data_field = 'date'
    x_label = 'Date'
    x_name = 'Date'
    aggregation_method = "last"

class StepView(BaseFitbitView):
    name = "steps"
    model = StepModel
    description = "Steps taken per day."
    y_label = "Steps"
    y_name = "Steps"

class DistanceView(BaseFitbitView):
    name = "distance"
    model = DistanceModel
    description = "Distance moved per day."
    y_label = "Distance"
    y_name = "Distance"

class TimeInBedView(BaseFitbitView):
    name = "time_in_bed"
    model = TimeInBedModel
    description = "Time in bed per day."
    y_label = "Time in bed"
    y_name = "Time in bed"

class MinutesAsleepView(BaseFitbitView):
    name = "minutes_asleep"
    model = MinutesAsleepModel
    description = "Sleep"
    y_label = "Minutes"
    y_name = "Minutes asleep"

class CaloriesView(BaseFitbitView):
    name = "calories"
    model = CaloriesModel
    description = "Exercise"
    y_label = "Calories"
    y_name = "Calories"

VIEW_DICT = {
    "activities/steps": StepView,
    "activities/distance": DistanceView,
    "sleep/timeInBed": TimeInBedView,
    "sleep/minutesAsleep": MinutesAsleepView,
    "activities/calories": CaloriesView,
}
