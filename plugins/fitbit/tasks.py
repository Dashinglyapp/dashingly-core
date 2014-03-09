from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.proxies import TaskProxy, MetricProxy
from core.plugins.lib.tasks import Interval, TaskBase
from plugins.facebook import manifest
from datetime import datetime, timedelta
from plugins.fitbit.models import MODEL_DICT
from dateutil import parser
import pytz

class ScrapeTask(TaskBase):
    interval = Interval.hourly
    task_proxy = TaskProxy(name="scrape")
    URL_BASE = "https://api.fitbit.com/1/user/-"
    DATE_MODELS = ["sleep/startTime"]

    def format_time(self, date):
        return date.strftime("%Y-%m-%d")

    def convert_time(self, date_string, timezone):
        date = parser.parse(date_string)
        date = date.replace(tzinfo=timezone)
        date = date.astimezone(pytz.utc)
        date = date.replace(tzinfo=None)
        return date

    def run(self):
        profile_url = "{0}/profile.json".format(self.URL_BASE)

        fitbit = self.auth_manager.get_auth("fitbit")
        profile = fitbit.get(profile_url).json()
        timezone = profile['user']['timezone']
        zone = pytz.timezone(timezone)

        for k in MODEL_DICT:
            model = MODEL_DICT[k]
            last_m = self.manager.query_last(manifest.plugin_proxy, model.metric_proxy)

            if last_m is None:
                last_time = self.format_time(datetime.now() - timedelta(days=365))
            else:
                last_time = self.format_time(last_m)

            url = "{0}/{1}/date/{2}/today.json".format(self.URL_BASE, k, last_time)
            data = fitbit.get(url).json()
            print data
            data = data[k.replace("/", "-")]

            for d in data:
                date_string = d.get('dateTime', None)

                value = d.get('value', None)
                if k in self.DATE_MODELS:
                    value = self.convert_time(value, zone)
                obj = model(
                    date=self.convert_time(date_string, zone),
                    value=value
                    )

                try:
                    self.manager.add(obj)
                except DuplicateRecord:
                    pass