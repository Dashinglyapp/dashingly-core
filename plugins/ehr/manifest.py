from core.plugins.lib.proxies import PluginProxy

NAME = "ehr"
HASHKEY = "ehr1"
DESCRIPTION = "Pulls in sample data from an ehr."

plugin_proxy = PluginProxy(name=NAME, hashkey=HASHKEY)