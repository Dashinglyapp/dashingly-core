from core.plugins.lib.base import BasePlugin
from core.plugins.lib.proxies import MetricProxy
from core.plugins.lib.permissions import AuthorizationPermission
from plugins.ehr.models import EHRData
from plugins.ehr.tasks import ImportTask
from plugins.ehr.views import EHRView
from datetime import datetime
from plugins.ehr import manifest

class EHRPlugin(BasePlugin):
    name = manifest.NAME
    description = manifest.DESCRIPTION
    models = [EHRData]
    tasks = [ImportTask]
    views = [EHRView]
    permissions = []
    hashkey = manifest.HASHKEY
    setup_task = ImportTask