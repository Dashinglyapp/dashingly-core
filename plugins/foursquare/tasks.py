from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.tasks import TaskBase, Interval
from core.plugins.lib.proxies import TaskProxy
from datetime import datetime, timedelta
from plugins.foursquare.models import Checkins
from core.plugins.lib.proxies import MetricProxy
from plugins.foursquare import manifest
import calendar
import pytz
from dateutil import parser, tz

class ScrapeTask(TaskBase):
    interval = Interval.hourly
    task_proxy = TaskProxy(name="scrape")

    def run(self):

        last_m = self.manager.query_last(manifest.plugin_proxy, MetricProxy(name="checkins"))
        if last_m is None:
            last_time = datetime.now().replace(tzinfo=pytz.utc) - timedelta(days=365)
        else:
            last_time = last_m.date.replace(tzinfo=pytz.utc)

        timestamp = calendar.timegm(last_time.timetuple())
        foursquare = self.auth_manager.get_auth("foursquare")
        token = foursquare.token
        token = token.replace("Bearer ", "")
        print(token)
        version = datetime.now().strftime("%Y%m%d")
        response = foursquare.get("https://api.foursquare.com/v2/users/self/checkins?afterTimestamp={0}&oauth_token={1}&v={2}".format(timestamp, token, version)).json()
        checkins = response['response']['checkins']['items']

        for c in checkins:
            if 'venue' in c:
                venue = c['venue']['name']
                location = c['venue']['location']
                latitude = location['lat']
                longitude = location['lng']
                visit_count = c['venue']['beenHere']['count']
            else:
                continue

            type = c['type']
            source = c['source']['name']
            created = c['createdAt']
            offset = c['timeZoneOffset']

            dt = datetime.fromtimestamp(created).replace(tzinfo=tz.tzoffset(None, offset))

            obj = Checkins(
                type=type,
                source=source,
                venue=venue,
                latitude=latitude,
                longitude=longitude,
                location=location,
                visit_count=visit_count,
                date=dt
            )

            try:
                self.manager.add(obj)
            except DuplicateRecord:
                pass