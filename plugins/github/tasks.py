from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.tasks import TaskBase, Interval
from core.plugins.lib.proxies import TaskProxy
from datetime import datetime, timedelta
from plugins.github.models import GithubCommits, DailyCommits
from core.plugins.lib.proxies import MetricProxy
from plugins.github import manifest
import pytz
from dateutil import parser

class ScrapeTask(TaskBase):
    interval = Interval.hourly
    task_proxy = TaskProxy(name="scrape")

    def run(self):

        last_m = self.manager.query_last(manifest.plugin_proxy, MetricProxy(name="commits"))
        if last_m is None:
            last_time = datetime.now().replace(tzinfo=pytz.utc) - timedelta(days=365)
        else:
            last_time = last_m.date.replace(tzinfo=pytz.utc)

        github = self.auth_manager.get_auth("github")
        user = github.get("https://api.github.com/user").json()
        repos = github.get(user['repos_url']).json()
        for r in repos:
            all_commits = []
            commit_url = "{0}/commits?since={1}".format(r['url'], last_time.isoformat())
            data = github.get(commit_url)
            commits = data.json()
            all_commits += commits
            while 'next' in data.links and data.links['next'] is not None and 'url' in data.links['next']:
                commit_url = data.links['next']['url']
                data = github.get(commit_url)
                commits = data.json()
                all_commits += commits

            user_commits = []
            for c in all_commits:
                if c is not None and 'author' in c and c['author'] is not None and 'id' in c['author']:
                    if c['author']['id'] == user['id']:
                        user_commits.append(c)

            for c in user_commits:
                obj = GithubCommits(
                    date=c['commit']['author']['date'],
                    repo_name=r['name'],
                    message=c['commit']['message'],
                    url=c['url'],
                    repo_url=r['url'])
                try:
                    self.manager.add(obj)
                except DuplicateRecord:
                    pass

            for c in user_commits:
                date = c['commit']['author']['date']
                date_obj = parser.parse(date)
                date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
                daily_commits = DailyCommits(date=date_obj, count=0)
                commits = self.manager.get_or_create(daily_commits)
                commits.count += 1
                self.manager.update(commits)