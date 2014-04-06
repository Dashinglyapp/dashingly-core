from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.correlator.models import Correlations, DirectionChanges
from plugins.correlator.tasks import CorrelationTask
from plugins.correlator.views import CorrelationView
from datetime import datetime
from plugins.correlator import manifest

class CorrelatorPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [Correlations, DirectionChanges]
    tasks = [CorrelationTask]
    views = [CorrelationView]
    permissions = []
    hashkey = manifest.HASHKEY
    setup_task = CorrelationTask