from core.plugins.lib.commands import BaseCommand
from plugins.test.manifest import plugin_proxy

class TestCommand(BaseCommand):
    name = "test"

    def run_command(self, **kwargs):
        print self.manager.query_filter(plugin_proxy)