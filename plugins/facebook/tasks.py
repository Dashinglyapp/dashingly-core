from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.proxies import TaskProxy, MetricProxy
from core.plugins.lib.tasks import Interval, TaskBase
from plugins.facebook import manifest
import pytz
from datetime import datetime, timedelta
from plugins.facebook.models import NewsFeed
from urlparse import urlparse, parse_qs
from calendar import timegm

class ScrapeTask(TaskBase):
    interval = Interval.hourly
    task_proxy = TaskProxy(name="scrape")

    def handle_stream_object(self, s):
        date = s.get('created_time', None)
        update_time = s.get('updated_time', None)
        from_id = s['from']['id']
        from_name = s['from']['name']
        story = s.get('story', None)
        type = s.get('type', None)

        likes = None
        if 'likes' in s:
            likes = s['likes']['data']

        comments = None
        if 'comments' in s:
            comments = s['comments']['data']

        message = s.get('message', None)
        name = s.get('name', None)
        shares = None
        if 'shares' in s:
            shares = s['shares']['count']

        picture = s.get('picture', None)
        obj = NewsFeed(
            date=date,
            update_time=update_time,
            from_id=from_id,
            from_name=from_name,
            story=story,
            type=type,
            likes=likes,
            comments=comments,
            message=message,
            name=name,
            shares=shares,
            picture=picture,
        )
        try:
            self.manager.add(obj)
        except DuplicateRecord:
            pass

    def get_data(self, facebook, url):
        data = facebook.get(url).json()
        if 'posts' in data:
            data = data['posts']
        return data

    def run(self):

        last_m = self.manager.query_last(manifest.plugin_proxy, MetricProxy(name="newsfeed"))
        if last_m is None:
            last_time = datetime.now() - timedelta(days=365)
        else:
            last_time = last_m.date
        last_stamp = timegm(last_time.utctimetuple())

        url = "https://graph.facebook.com/me?fields=posts.since({0})".format(last_time.isoformat())
        facebook = self.auth_manager.get_auth("facebook")

        data = self.get_data(facebook, url)
        streams = []
        next_page = True
        until_under = False
        while next_page:
            pages = data.get('paging', None)
            stream = data.get('data', None)
            if stream is None:
                break

            streams += stream
            if pages is None:
                next_page = False
            else:
                url = pages['next']
                until = int(parse_qs(urlparse(url).query)['until'][0])
                if until < last_stamp:
                    if not until_under:
                        until_under = True
                    else:
                        next_page = False
                data = self.get_data(facebook, url)
                if len(data['data']) < 0:
                    next_page = False

        for s in streams:
            try:
                self.handle_stream_object(s)
            except KeyError:
                continue