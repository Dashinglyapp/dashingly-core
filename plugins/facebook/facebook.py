from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.facebook import manifest
from plugins.facebook.tasks import ScrapeTask
from plugins.facebook.models import NewsFeed
from datetime import datetime
from plugins.facebook.views import FacebookView


class FacebookPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [NewsFeed]
    permissions = [AuthorizationPermission(name="facebook")]
    hashkey = manifest.HASHKEY
    tasks = [ScrapeTask]
    setup_task = ScrapeTask
    views = [FacebookView]