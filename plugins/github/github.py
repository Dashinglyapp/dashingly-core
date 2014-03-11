from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.github.models import GithubCommits
from plugins.github.tasks import ScrapeTask
from plugins.github.views import GithubView
from datetime import datetime
from plugins.github import manifest

class GithubPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [GithubCommits]
    tasks = [ScrapeTask]
    views = [GithubView]
    permissions = [AuthorizationPermission(name="github")]
    hashkey = manifest.HASHKEY
    setup_task = ScrapeTask