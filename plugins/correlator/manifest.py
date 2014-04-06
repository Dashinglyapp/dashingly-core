from core.plugins.lib.proxies import PluginProxy

NAME = "correlator"
HASHKEY = "correlator1"
DESCRIPTION = "Pulls in sample data from an ehr."

plugin_proxy = PluginProxy(name=NAME, hashkey=HASHKEY)