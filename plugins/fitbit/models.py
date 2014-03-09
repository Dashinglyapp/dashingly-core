from core.plugins.lib.proxies import MetricProxy, SourceProxy
from core.plugins.lib.models import PluginDataModel
from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField, IntegerField
from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

class BaseFitbitModel(PluginDataModel):
    metric_proxy = MetricProxy(name="newsfeed")
    source_proxy = SourceProxy(name="fitbit")

    date = DateTimeField()
    value = FloatField()

class StepModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="steps")

class DistanceModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="distance")

class TimeInBedModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="time_in_bed")

class MinutesAsleepModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="minutes_asleep")

class WeightModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="weight")

class SleepEfficiencyModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="sleep_efficiency")

class ActivityCaloriesModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="activity_calories")

class SleepStartTimeModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="sleep_start_time")
    value = DateTimeField()

class CaloriesInModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="calories_in")

class CaloriesModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="calories")

class WaterModel(BaseFitbitModel):
    metric_proxy = MetricProxy(name="water")

MODEL_DICT = {
    "activities/steps": StepModel,
    "activities/distance": DistanceModel,
    "sleep/timeInBed": TimeInBedModel,
    "sleep/minutesAsleep": MinutesAsleepModel,
    "body/weight": WeightModel,
    "sleep/efficiency": SleepEfficiencyModel,
    "activities/activityCalories": ActivityCaloriesModel,
    "sleep/startTime": SleepStartTimeModel,
    "foods/log/caloriesIn": CaloriesInModel,
    "activities/calories": CaloriesModel,
    "foods/log/water": WaterModel
}
