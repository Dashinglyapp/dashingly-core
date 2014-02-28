from core.plugins.base import BasePlugin
from core.plugins.proxies import MetricProxy
from core.plugins.permissions import AuthorizationPermission
from plugins.github.models import GithubCommits, DailyCommits
from plugins.github.tasks import ScrapeTask
from datetime import datetime
from plugins.github import manifest

class GithubPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [GithubCommits, DailyCommits]
    tasks = [ScrapeTask]
    permissions = [AuthorizationPermission(name="github")]
    hashkey = manifest.HASHKEY

    def setup(self):
        pass

    def destroy(self):
        pass

    def save_forms(self, metric, **kwargs):
        pass