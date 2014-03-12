Our first plugin
---------------------------------------

Given how important plugins are to Realize, we would be remiss not to walk you through making one!  This guide assumes some knowledge of Python, familiarity with object oriented program, and some familiarity with git/Github.

Let's say that one day you get curious, and want to know how much you are committing to Github.  Naturally, you would decide to write a Realize plugin to do this for you.  In order to build your plugin, you would need some way to authenticate with Github, some way to import your data, and some way to display that data.  Let's go through how you would make a plugin to do that.

First steps
======================================

Our first step is to decide on a plugin name.  Being super original, let's pick the name `github`.  We can now create a folder for our plugin at `realize-core/plugins/github`.

We are now ready to define a main plugin class.  We will need to make a file to put this in.  The file should have the same name as our plugin, so we should put it at `realize-core/plugins/github/github.py`.  We can then define the plugin class inside the file.

All main plugin classes inherit from `core.plugins.lib.base.BasePlugin`.

This class defines some metadata about our plugin.

.. code-block:: python

    from core.plugins.lib.base import BasePlugin

    class GithubPlugin(BasePlugin):
        pass


Great!  Now we have a plugin class.  The class will contain a lot of metadata about our plugin eventually, but for now, we only need to worry about 3 parameters: name, hashkey, and description.  We already have our name -- its `github`.  The description can be any text describing the plugin.  The hashkey is a little more complex, but it just has to be any globally unique string (unique across all plugins).  We don't have a plugin directory yet to assign hashkeys, so appending some text to the name of the plugin will be sufficient for now.

.. code-block:: python

    from core.plugins.lib.base import BasePlugin

    class GithubPlugin(BasePlugin):
        name = "github"
        description = "An example github plugin."
        hashkey = "github_hashkey"

This is actually all we need for Realize to pick up and load the plugin, but it unfortunately doesn't do anything yet.  The following sections will get more in depth.

Creating models
===========================================

Models give plugins a way to store data flexibly.  If you are familiar with ORMs, these models are very similar.  You essentially pick the data you want to store, and then create a model with those attributes.  This allows us to abstract away the details of the database, while still giving the plugin a lot of control over data manipulation.  Models inherit from `core.plugins.lib.models.PluginDataModel`.

Since we will be storing github commits, we want to store things like commit message, commit time, and repo name. If you have never seen what commits look like on github, check `these out <https://github.com/realizeapp/realize-core/commit/559a285f30cca822336d7de03daa0d1aeb91ef96>`_.

 We can specify these as fields.  Fields inherit from one of the classes in `core.plugins.lib.fields`.  Fields allow Realize to properly store the data.  Each time we wanted to store a commit, we would create a new model, set the values of the fields, and then save the model.

.. code-block:: python

    from core.plugins.lib.models import PluginDataModel
    from core.plugins.lib.fields import Field, DateTimeField

    class GithubCommits(PluginDataModel):
        date = DateTimeField()
        repo_name = Field()
        repo_url = Field()
        message = Field()
        url = Field()

This will let us store the information associated with a commit properly.  The basic `Field` will store string values, and `DateTimeField` will store datetime objects properly.  There are other fields to store other types of data.

Metrics
++++++++++++++++++++++++++++++++++++++

But wait!  There are a few more fields we need to add to a model.  Every model needs to specify what metric it measures.  These are specified through `MetricProxy` classes:

.. code-block:: python

    from core.plugins.lib.proxies import MetricProxy
    metric_proxy = MetricProxy(name="commits")

This allows other plugins to easily reference the data, and for data to be normalized across plugins (for example, sleep data coming from multiple plugins could have the same metric name).  A plugin should only have one model with the same metric name.

Sources
+++++++++++++++++++++++++++++++++++++++

We also need to define a source, which is defined through a `SourceProxy` class:

.. code-block:: python

    from core.plugins.lib.proxies import SourceProxy
    source_proxy = SourceProxy(name="github")

Sources allow Realize to easily figure out what data came from where, and to display that to the user.

Permissions
+++++++++++++++++++++++++++++++++++++++++

We also need to specify who can access the data in the model.  This is done through a scope class.  An example scope class would be `Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))`.  Each scope contains a zone and a block.  Zones define `who` can access the data, whereas blocks define `what` can access the data.

Zones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A zone class is a string of who can access the resource, and then one of many optional arguments.  There are six possible combinations:

 - `ZonePerm("user", current=True)` means that the current user can access the data.  So the user that creates the data can see the data, and nobody else.
 - `ZonePerm("user", all=True)` means all users on the server can see the data.
 - `ZonePerm("user", key=USER_KEY)` means that the user with the given key can access the data.
 - `ZonePerm("group", current=True)` means that only the current group can access the data.  So the group that creates the data can see it, but nobody else.
 - `ZonePerm("group", all=True)` means that all groups that the user is part of can see the data.
 - `ZonePerm("group", key=GROUP_KEY)` means that the group with the given key can see the data

Blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A block is a string of what can access the resource, and then optional arguments.  There are three combinations.

 - `BlockPerm("plugin", current=True)` means that the current plugin can access the data. Only the plugin that creates the data can see it.
 - `BlockPerm("plugin", all=True)` means all plugins can access the data.
 - `BlockPerm("plugin", key=PLUGIN_KEY)` means that the given plugin can access the data.

Scopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scopes, as we saw before, are a combination of zone and block.  So `Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))` means that only the plugin that created the data for the current user can access the data. `Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))` means that any plugins the current user has installed can access the data. `Scope(ZonePerm("group", all=True), BlockPerm("plugin", all=True))`  means that any plugin installed by anybody in any group the user is in can access the data.

 The default scope for a model is `Scope(ZonePerm("user", current=True), BlockPerm("plugin", current=True))`.

Our permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: python

    from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm
    perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

We are going to let any plugin the current user has installed access the data.  As you see, permissions are a list, which allows for multiple scopes to be used side by side.

Complete Model
+++++++++++++++++++++++++++++++++++++++++++++

Whew!  After all of that work, our model looks like this:

 .. code-block:: python

    from core.plugins.lib.proxies import MetricProxy, SourceProxy
    from core.plugins.lib.models import PluginDataModel
    from core.plugins.lib.fields import Field, ListField, DateTimeField, FloatField
    from core.plugins.lib.scope import Scope, ZonePerm, BlockPerm

    class GithubCommits(PluginDataModel):
        metric_proxy = MetricProxy(name="commits")
        source_proxy = SourceProxy(name="github")
        perms = [Scope(ZonePerm("user", current=True), BlockPerm("plugin", all=True))]

        date = DateTimeField()
        repo_name = Field()
        repo_url = Field()
        message = Field()
        url = Field()

Creating tasks
============================================

So we have a way to store the data.  Great, but where are we going to get it from.  From github, of course!  This will require a couple of things.  First, we need to get an authorization that lets the plugin connect to Github on our behalf.  We also need a periodic task that runs and grabs data from Github.

Authorization
+++++++++++++++++++++++++++++++++++++++++++++

The first item can be accomplished with `Oauth <http://oauth.net/>`_.  Oauth specifies a way for tools to connect to oauth providers on behalf of a user and perform actions that they were given permission to do.  Oauth can get complicated and hairy.  Luckily, Realize takes care of taking the user through the oauth process and storing their information.  All a plugin needs to do is request permission to access the credentials.  Awesome, right?

In our main plugin class, we need to add the line: `permissions = [AuthorizationPermission(name="github")]`.  This indicates that the plugin is asking for permission to access the users authorization with github.  Now, it's just a matter of inserting `github = self.auth_manager.get_auth("github")` somewhere in the code to get a fully functional github client that can make requests on behalf of the user.

Tasks
++++++++++++++++++++++++++++++++++++++++++++++

Now that authorization is out of the way, we can focus on tasks.  Tasks will let us periodically get data from Github.  All tasks inherit from `core.plugins.lib.tasks.TaskBase`.  Tasks need to specify an interval at which they run (hourly, daily, or weekly), and a name through a `TaskProxy`

 .. code-block:: python

    class ScrapeTask(TaskBase):
        interval = Interval.hourly
        task_proxy = TaskProxy(name="scrape")

        def run(self):
            pass

Querying the database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The above task will be run hourly.  We will fill in the `run` method with our task-specific logic.  We want to add code to scrape github and store the data to our model.  Assume that any code in this section after here is in the `run` method.

 .. code-block:: python

    last_m = self.manager.query_last(PluginProxy(hashkey="github_hashkey", name="github"), MetricProxy(name="commits"))
    if last_m is None:
        last_time = datetime.now().replace(tzinfo=pytz.utc) - timedelta(days=365)
    else:
        last_time = last_m.date.replace(tzinfo=pytz.utc)

The manager is a special attribute that is set by the runtime when the task is loaded.  It allows the task to access the database in a controlled way.  In the above query, we are looking for the last of our GithubCommits models.  Each plugin and metric combo is unique, so our query will only return those elements.  If there aren't any, we will set our time to one year ago.  We are going to use the last time to get any commits to Github on or after that time, so this will allow us to scrape one year's worth of Github data initially.

Getting the data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can now query github for the information we want:

 .. code-block:: python

    github = self.auth_manager.get_auth("github")
    user = github.get("https://api.github.com/user").json()
    repos = github.get(user['repos_url']).json()

This gets the right client from the auth manager, and then uses it to query github.  We can then grab all of the repositories that the user owns.

For each repo, we grab all of the commits

 .. code-block:: python

    commit_url = "{0}/commits?since={1}".format(r['url'], last_time.isoformat())
    commits = github.get(commit_url).json()

Notice how we use our last time parameter.

Storing the data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can then loop through each commit and store it:

 .. code-block:: python

    obj = GithubCommits(
        date=c['commit']['author']['date'],
        repo_name=r['name'],
        message=c['commit']['message'],
        url=c['url'],
        repo_url=r['url'])
    try:
        self.manager.add(obj)
    except DuplicateRecord:
        pass

This creates a GithubCommits model, and adds it to our manager (which saves it).  If the model already exists, we catch the DuplicateRecord exception and keep going.

Creating Views
================================================

Cool, so we can get our data and store it.  Now, we need a way to show it to the user.  This is where views come in.  Views are python classes that define methods, like `get`, `post`, `put`, `patch`, and `delete`.  Each of these methods corresponds to an HTTP method, and each view has its own unique URL.  This allows you to do cool things like post data from a phone app to Realize, or get insights back.  Right now, it allows us to create a way to surface our github commit data.

When you create a view, you can either inherit from the basic `BaseView` class at `core.plugins.lib.views.base.BaseView`, which will let you customize the view as much as you want, or inherit from one of the more structured views in the other modules at `core.plugins.lib.views`.

We will be inheriting from `core.plugins.lib.views.charts.DailyCountChartView`.  This is a structured daily count chart that won't require much work from us to get started with.

 .. code-block:: python

    from core.plugins.lib.views.charts import DailyCountChartView

    class DailyCommitChart(DailyCountChartView):
        name = 'daily_commits'
        description = 'How many commits you made in github per day.'
        model = GithubCommits
        y_data_field = 'data'
        x_data_field = 'date'
        y_label = 'Commit count'
        x_label = 'Date'
        x_name = 'Date'
        y_name = 'Daily commits'
        x_data_field = 'date'

This view will surface an API route with the daily commit history.  Any frontend will be able to pick up and render this.  You can find the unique hashkey and URL to a view through the API browser (covered earlier in the documentation).

Wrapping up
=====================================================

Our plugin now does everything we set out to do!  High fives all around.  We just need to do one last thing to pull everything together.  We need to add the views and models to the main plugin class so that Realize knows they exist.

 .. code-block:: python

    from core.plugins.lib.base import BasePlugin
    from core.plugins.lib.proxies import MetricProxy
    from core.plugins.lib.permissions import AuthorizationPermission

    class GithubPlugin(BasePlugin):
        name = "github"
        description = "An example github plugin."
        hashkey = "github_hashkey"
        permissions = [AuthorizationPermission(name="github")]
        models = [GithubCommits]
        tasks = [ScrapeTask]
        views = [DailyCommitChart]
        setup_task = ScrapeTask

This registers our model, task, and view.  We also add ScrapeTask as a setup_task.  This ensures that when a user installs the plugin, that task is run.  This is nice if you want to give users instant data.

To see all of the code, check out `plugins/github`.  It has been split into multiple files there, but the logic is all the same.
