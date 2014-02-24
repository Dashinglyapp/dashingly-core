from core.plugins.base import BasePlugin
from datetime import datetime

class TestPlugin(BasePlugin):
    name = "Test"
    description = "Desc"
    hashkey = "Hashkey"
    models = []
    forms = []
