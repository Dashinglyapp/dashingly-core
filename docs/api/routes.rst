API Routes
---------------------------------------------

Note:  These may be out of date.  The browsable API and spec are the best resources for this.

API Versions
===================================================

The current API version is one.  Please prefix all URLs with `/api/v1`.

Top Level URLs
===================================================

* `/login` GET request will get the login form, POST to login and get an auth token.
* `/register` GET will get the signup form, POST to register and get an auth token.
* `/logout` GET will logout.
* `/auth_check` POST will check on the authentication of the user.  Use `token` as the parameter to pass the auth token.
* `/tasks/TASK_ID` GET will show the status of the given task.  Tasks are used for things like setup of a plugin. Task status URLs are passed back when a plugin is installed or removed.

Oauth
+++++++++++++++++++++++++++++++++++++++++++++++++++

Oauth login URLs like `/oauth/github/login` can be hit with a GET request to start the Oauth process.  After finishing the process, users will be redirected to `/authorizations`.

Scoping
===================================================

Most URLs require a scope.  Scopes define who the URL is associated with by specifying the type of object, and a unique id for it.

The type of object can be 'user' or 'group'.  The unique id (hashkey) specifies which user or group you are operating on.  The general format is `/API_VERSION/TYPE/KEY/ACTION`.  For example, a valid URL to get a list of views would be `/api/v1/user/USER_HASHKEY/views`.  Similarly, for a group, it would be `/api/v1/group/GROUP_HASHKEY/views`.

API version and scope should be prepended to all the URLs after this point.

Shared scoped URLs
===================================================

All of these URLs start with `/api/v1/group/GROUP_HASHKEY` or `/api/v1/user/USER_HASHKEY`.

Top level
+++++++++++++++++++++++++++++++++++++++++++++++++++

* `/views` GET will get a listing of all the views available.  This will include URLs for individual views.
* `/plugins/manage` GET will show a listing of all plugins
* `/resources` GET will show you a list of all resources and their settings URLs.  POST will create a new resource with specified parameters `name` (string), `type` (string), and `settings` (json object).

Second level
+++++++++++++++++++++++++++++++++++++++++++++++++++

Views
~~~~~~~~~~~~~~~~~~~~~~

Views have specific URLs that allow for data extraction, saving, and so on.  Support for methods varies, but all will support GET, and some will support POST as well.  A sample view url is `/plugins/gh55hjghgh44/views/eb35a77988996b002739`.  The format is `plugins/PLUGIN_HASHKEY/views/VIEW_HASHKEY`.

Plugin Management
~~~~~~~~~~~~~~~~~~~~~~

* `/plugins/PLUGIN_HASHKEY/actions/add` Add the plugin to the specified scope object. GET only.
* `/plugins/PLUGIN_HASHKEY/actions/remove` Remove the plugins from the specified scope object. GET only.
* `/plugins/PLUGIN_HASHKEY/actions/configure` Configure the specified plugin.  GET will get the form representation, and POST will save the new settings.

Resources
~~~~~~~~~~~~~~~~~~~~~~

Frontend resources have their own settings URLs that look like `/resources/RESOURCE_HASHKEY`.  A GET request will pull the settings for the resource with that name for the current scope and return them (will return {} if there are no settings).  A PUT request will update the settings.  DELETE will remove the settings.

For example, if you want to store settings for a resource with name `test` and type `dashboard`, you would POST to `/resources` with this data:

.. code-block:: shell

    {
    "settings": {
      "1":"1",
      "2":"2"
    },
    "name": "test",
    "type": "dashboard"
    }


The next time you do a GET request, you would receive:

.. code-block:: shell

    {
        "meta": {
            "code": 200
        },
        "settings": {
            "1": "1",
            "2": "2"
        },
        "name": "resource_data",
        "tags": null
    }

Group Scoped URLs
===================================================

All of these URLs start with `/api/v1/group/GROUP_HASHKEY`.

List Views
+++++++++++++++++++++++++++++++++++++++++++++++++++

`api/v1/group` GET will return a list of all groups.  POST will create a new group.

Detail Views
+++++++++++++++++++++++++++++++++++++++++++++++++++

Groups have their own detail views and actions.  Hitting `/api/v1/group/GROUP_HASHKEY` with a GET request will give you the information for that group.

User Scoped URLs
===================================================

All of these URLs start with `/api/v1/user/USER_HASHKEY`.

Top Level
+++++++++++++++++++++++++++++++++++++++++++++++++++

* `/groups` GET will show you a list of all groups you are in.  POST will create a new group with the specified `name` and `description`.
* `/authorizations` GET will show a listing of all available authorization methods and a url to send the user to to complete them.

Profile
+++++++++++++++++++++++++++++++++++++++++++++++++++

The user has a profile, and its attributes can be accessed and modified via `/profile`.  This endpoint supports GET and POST.  A GET request will return typical form data.

To save data, POST data in this format:

.. code-block:: shell

    {
      "timezone": "test",
      "first_name": "test",
      "last_name": "test",
      "settings": {
        "test" : "test"
      }

    }

Groups
+++++++++++++++++++++++++++++++++++++++++++++++++++

`/groups/GROUP_HASHKEY/add` GET will add you to the specified group.
`/groups/GROUP_HASHKEY/remove` will remove you from the specified group.