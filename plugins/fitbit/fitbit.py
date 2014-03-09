from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.fitbit import manifest
from datetime import datetime
from plugins.fitbit.tasks import ScrapeTask
from plugins.fitbit.models import MODEL_DICT
from plugins.fitbit.views import VIEW_DICT

class FitbitPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [MODEL_DICT[k] for k in MODEL_DICT]
    permissions = [AuthorizationPermission(name="fitbit")]
    hashkey = manifest.HASHKEY
    tasks = [ScrapeTask]
    setup_task = ScrapeTask
    views = [VIEW_DICT[k] for k in VIEW_DICT]