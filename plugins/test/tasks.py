from core.plugins.models import DuplicateRecord
from core.plugins.tasks import TaskBase, Interval
from core.plugins.proxies import TaskProxy
from datetime import datetime, timedelta
from models import GithubCommits
from core.plugins.proxies import MetricProxy
import manifest
import pytz


class ScrapeTask(TaskBase):
    interval = Interval.hourly
    task_proxy = TaskProxy(name="scrape")

    def run(self):

        last_m = self.manager.query_blob_last(manifest.plugin_proxy, MetricProxy(name="commits"))
        if last_m is None:
            last_time = datetime.now().replace(tzinfo=pytz.utc) - timedelta(days=365)
        else:
            last_time = last_m.date.replace(tzinfo=pytz.utc)

        print last_time

        github = self.auth_manager.get_auth("github")
        user = github.get("https://api.github.com/user").json()
        repos = github.get(user['repos_url']).json()
        for r in repos:
            all_commits = []
            commit_url = "{0}/commits?since={1}".format(r['url'], last_time.isoformat())
            data = github.get(commit_url)
            commits = data.json()
            all_commits += commits
            while hasattr(data.links, "next"):
                commit_url = data.links['next']
                data = github.get(commit_url)
                commits = data.json()
                all_commits += commits

            user_commits = []
            for c in commits:
                if 'author' in c and 'id' in c['author']:
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






