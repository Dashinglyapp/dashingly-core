class Perm(object):
    def __init__(self, scope, key=None, all=False, current=False):
        self.key = key
        self.scope = scope
        self.all = all
        self.current = current

    def __repr__(self):
        return "<Perm(key='%s', scope='%s', all='%s' current='%s')>" % (self.key, self.scope, self.all, self.current)

class ZonePerm(Perm):
    """
    Permission grants for user data.
    First value is the type of zone to grant access to.  One of "user" or "group".
    Second is which members of the zone to give access to.  Either the id of a zone member, "all", or "current".
    ZonePerm("user", "USER_ID")
    ZonePerm("user", "all")
    ZonePerm("user", "current")
    """
    pass

class BlockPerm(Perm):
    """
    Permission grants for user data.
    First value is the type of block to grant access to.  Currently can only be "plugin".
    Second is which members of the block to give access to.  Either the id of a block member, "all", or "current".
    BlockPerm("plugin", "PLUGIN_ID")
    BlockPerm("plugin", "current")
    """
    pass

class Scope(object):
    """
    A scope tuple corresponding to what permissions the model is granting to others.
    Examples are:
    Scope(ZonePerm("user", "current"), BlockPerm("plugin", "current")) -- this would
    give the current plugin installed by the current user access to the given model (this is not so useful,
    as the plugin defining the model already has access to it!)

    Scope(ZonePerm("user", "current"), BlockPerm("plugin", "all")) -- Allows any plugin installed by the current user to access the data.

    Scope(ZonePerm("user", "all"), BlockPerm("plugin", "all")) -- Allows any plugin installed by any user to access the data.

    Scope(ZonePerm("user", "USER_ID"), BlockPerm("plugin", "PLUGIN_ID")) -- Allows the specified plugin, installed by the specified user, to access the data.
    """
    def __init__(self, zone, block):
        self.zone = zone
        self.block = block

class TaskScope(object):
    """
    Zone is one of "user", "group", or "all".  Indicates what level of entity the task is operating on.
    """
    def __init__(self, zone):
        self.zone = zone
