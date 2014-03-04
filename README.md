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

Get some food. You have time. An hour or so later it should finish.

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

How to Login and get auth token
---------------------------------------------

Send a GET request to `/login` with `Content-Type` set to `application/json`.

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

Now we can request form data by sending a GET request to `/forms` with the `Authentication-Token` header set to `WyIxIiwiMm` and the `Content-Type` header set to `application/json`.

How to register
---------------------------------------------

Send a GET request to `/register` with `Content-Type` set to `application/json`.

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

API Endpoint Listing
---------------------------------------------

## Top level

`/login` GET request will get the login form, POST to login and get an auth token.
`/register` GET will get the signup form, POST to register and get an auth token.
`/logout` GET will logout.
`/views` GET will get a listing of all the views available.  This will include URLs for individual widgets.
`/authorizations` GET will show a listing of all available authorization methods and a url to send the user to to complete them.
`/plugins/manage` GET will show a listing of all plugins

## Second level

Widget views are URLs specific to each widget that allow for data extraction, saving, and so on.  Support for methods varies, but all will support GET, and some will support POST as well.  A sample widget url is `/plugins/1/views/eb35a77988996b002739`.  The format is `plugins/PLUGIN_HASHKEY/views/VIEW_HASHKEY`.

`/plugins/1/actions/add` and `/plugins/1/actions/remove` allow you to add and remove plugins from the user list.  The format is `plugins/PLUGIN_HASHKEY/actions/ACTION_NAME`.  These two only support GET requests.  A third plugin management URL, `/plugins/1/actions/configure`, will GET form data, and POST will save the data.

Oauth login URLs like `/oauth/github/login` can be hit with a GET request to start the Oauth process.  After finishing the process, users will be redirected to `/authorizations`.

