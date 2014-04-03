from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.foursquare.models import Checkins
from plugins.foursquare.tasks import ScrapeTask
from datetime import datetime
from plugins.foursquare import manifest
from plugins.foursquare.views import CheckinMap

class FoursquarePlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [Checkins]
    tasks = [ScrapeTask]
    views = [CheckinMap]
    permissions = [AuthorizationPermission(name="foursquare")]
    hashkey = manifest.HASHKEY
    setup_task = ScrapeTask