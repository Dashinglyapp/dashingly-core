from core.plugins.proxies import PluginProxy

NAME = "github"
HASHKEY = "github1"
DESCRIPTION = "Pulls your commit history our of github."

plugin_proxy = PluginProxy(name=NAME, hashkey=HASHKEY)