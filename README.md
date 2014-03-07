This is a minimal and work-in-progress version of [Realize](http://www.realize.pe).

[![Build Status](https://travis-ci.org/realizeapp/realize-core.png?branch=master)](https://travis-ci.org/realizeapp/realize-core)

Get started with Vagrant
----------------------------------------

The easiest way to get started is with a Vagrant virtual machine:

First, [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads).

Next [Install Vagrant](http://www.vagrantup.com/downloads)

Then type:
```sh
vagrant up
```

This should take 15-20 minutes to download and install dependencies on newer machines.

Then type:

```sh
vagrant ssh
cd /vagrant
python app.py
```

Vagrant forwards port 5000 in VirtualBox to [http://localhost:8080](http://localhost:8080) on your host machine, so you should be able to click the link and see the Realize UI.  Vagrant keeps folders in sync, so editing things in the project folder will cause the changes to be mirrored and reloaded in Vagrant automatically.

If you want to run delayed tasks, open another ssh connection: (note to self: reconsider the name "delayed" if there are different types of delayed tasks)

```
vagrant ssh
cd /vagrant
celery -A app.celery worker --loglevel=debug -B
```


Get started manually (only recommended for Linux)
-----------------------------------------

Manual setup:

```
cd realize-core
sudo xargs -a apt-packages.txt apt-get install
pip install -r requirements.txt
alembic upgrade head
```

General usage
------------------------------------------

Usage (webserver):

```
python app.py
```

Usage (tasks):

```
celery -A app.celery worker --loglevel=debug -B
```

Create migrations (if you change core/database/models.py):

```
alembic revision --autogenerate -m "MESSAGE HERE"
```

Run tests:

```
nosetests --with-coverage --cover-package="core" --logging-level="INFO"
```

Authentication
---------------------------------------------

## Login

Send a GET request to `/api/v1/login` with `Content-Type` set to `application/json`.

You will get something like this (some fields omitted):

```
{
  "csrf_token": "1393947811.08##753ae77ee60910969074a614d70708c513053578",
  "fields": [
    {
      "data": null,
      "default": null,
      "description": "",
      "errors": [],
      "flags": {},
      "id": "email",
      "label": "<label for=\"email\">Email Address</label>",
      "name": "email",
      "object_data": null,
      "raw_data": null,
      "short_name": "email",
      "type": "TextField",
      "widget": {}
    },
  ]

```

Then POST with `Content-Type` set to `application/json` and the `X-CSRFToken` header set to `csrf-token` from the above response.  Use properly formatted JSON for the body.

Sample JSON for login:
```
{
"email": "test@realize.pe",
"password": "test"
}
```

You will now get an authentication token:

```
{
    "meta": {
        "code": 200
    },
    "response": {
        "user": {
            "authentication_token": "WyIxIiwiMm",
            "id": "1"
        }
    }
}
```

Use the token in the header with all requests to resources where the user needs to be logged in.  Set the `Authentication-Token` header to the value of the token.  This token will expire after 1 week.  The client should get a new token when this happens.

## Verify token

If you want to check the validity of an auth token, you can POST to `/api/v1/auth_check` with the `token` parameter set to the token.  You will receive the authentication status and user hashkey.

## Register

Send a GET request to `/api/v1/register` with `Content-Type` set to `application/json`.

You will receive similar output to the login request.

Then do a POST request with the `X-CSRF-Token` and `Content-Type` headers set.

```
{
"email": "test1@realize.pe",
"password": "test"
}
```

You will receieve an auth token:

```
{
    "meta": {
        "code": 200
    },
    "response": {
        "user": {
            "authentication_token": "WyI0",
            "id": "4"
        }
    }
}
```

Top level API
---------------------------------------------

## API Versions

The current API version is one.  Please prefix all URLs with `/api/v1`.

## Top Level URLs

* `/login` GET request will get the login form, POST to login and get an auth token.
* `/register` GET will get the signup form, POST to register and get an auth token.
* `/logout` GET will logout.
* `/auth_check` POST will check on the authentication of the user.  Use `token` as the parameter to pass the auth token.
* `/tasks/TASK_ID` GET will show the status of the given task.  Tasks are used for things like setup of a plugin. Task status URLs are passed back when a plugin is installed or removed.

### Oauth

Oauth login URLs like `/oauth/github/login` can be hit with a GET request to start the Oauth process.  After finishing the process, users will be redirected to `/authorizations`.

Scoping
-----------------------------------------------

## Scopes

Most URLs require a scope.  Scopes define who the URL is associated with by specifying the type of object, and a unique id for it.

The type of object can be 'user' or 'group'.  The unique id (hashkey) specifies which user or group you are operating on.  The general format is `/API_VERSION/TYPE/KEY/ACTION`.  For example, a valid URL to get a list of views would be `/api/v1/user/USER_HASHKEY/views`.  Similarly, for a group, it would be `/api/v1/group/GROUP_HASHKEY/views`.

API version and scope should be prepended to all the URLs after this point.

Shared scoped URLs
------------------------------------------------

All of these URLs start with `/api/v1/group/GROUP_HASHKEY` or `/api/v1/user/USER_HASHKEY`.

## Top level

* `/views` GET will get a listing of all the views available.  This will include URLs for individual views.
* `/plugins/manage` GET will show a listing of all plugins
* `/resources` GET will show you a list of all resources and their settings URLs.  POST will create a new resource with specified parameters `name` (string), `type` (string), and `settings` (json object).

## Second level

### Views

Views have specific URLs that allow for data extraction, saving, and so on.  Support for methods varies, but all will support GET, and some will support POST as well.  A sample view url is `/plugins/gh55hjghgh44/views/eb35a77988996b002739`.  The format is `plugins/PLUGIN_HASHKEY/views/VIEW_HASHKEY`.

### Plugin Management

* `/plugins/PLUGIN_HASHKEY/actions/add` Add the plugin to the specified scope object. GET only.
* `/plugins/PLUGIN_HASHKEY/actions/remove` Remove the plugins from the specified scope object. GET only.
* `/plugins/PLUGIN_HASHKEY/actions/configure` Configure the specified plugin.  GET will get the form representation, and POST will save the new settings.

### Resources

Frontend resources have their own settings URLs that look like `/resources/RESOURCE_HASHKEY`.  A GET request will pull the settings for the resource with that name for the current scope and return them (will return {} if there are no settings).  A PUT request will update the settings.  DELETE will remove the settings.

For example, if you want to store settings for a resource with name `test` and type `dashboard`, you would POST to `/resources` with this data:

```
{
"settings": {
  "1":"1",
  "2":"2"
},
"name": "test",
"type": "dashboard"
}
```

The next time you do a GET request, you would receive:

```
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
```

Group Scoped URLs
-------------------------------------------------------------

All of these URLs start with `/api/v1/group/GROUP_HASHKEY`.

## List Views

`api/v1/group` GET will return a list of all groups.  POST will create a new group.

## Detail Views

Groups have their own detail views and actions.  Hitting `/api/v1/group/GROUP_HASHKEY` with a GET request will give you the information for that group.

User Scoped URLs
-------------------------------------------------------------

All of these URLs start with `/api/v1/user/USER_HASHKEY`.

## Top Level

* `/groups` GET will show you a list of all groups you are in.  POST will create a new group with the specified `name` and `description`.
* `/authorizations` GET will show a listing of all available authorization methods and a url to send the user to to complete them.

## Profile

The user has a profile, and its attributes can be accessed and modified via `/profile`.  This endpoint supports GET and POST.  A GET request will return typical form data.

To save data, POST data in this format:

```
{
  "timezone": "test",
  "first_name": "test",
  "last_name": "test",
  "settings": {
    "test" : "test"
  }

}
```

## Groups

`/groups/GROUP_HASHKEY/add` GET will add you to the specified group.
`/groups/GROUP_HASHKEY/remove` will remove you from the specified group.