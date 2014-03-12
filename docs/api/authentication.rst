Authentication
----------------------------------------------------

The API requires an authentication token for (most) views.  This section will show you how to register and login.

Register
=====================================================

Send a GET request to `/api/v1/register` with `Content-Type` set to `application/json`.

You will get something like this (some fields omitted):

.. code-block:: shell

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
    }

Then POST with `Content-Type` set to `application/json` and the `X-CSRFToken` header set to `csrf-token` from the above response.  Use properly formatted JSON for the body.

Sample JSON for registration:

.. code-block:: shell

    {
    "email": "test1@realize.pe",
    "password": "test11"
    }


You will receieve an auth token and a hashkey:

.. code-block:: shell

    {
      "user": {
        "hashkey": "df3cf9ecb8e65b53e1b4c6492e70eff8",
        "id": "1",
        "token": "WyIxIiwiNmVjOGMwOWQxY2JmMmUwZDVkODFkZWI0ZjgxYjhiNzciXQ.Bf54QQ.3xKpx9C_5gskeu3vJx_ytkgXU6c"
      }
    }


Use the token in the header with all requests to resources where the user needs to be logged in.  Set the `Authentication-Token` header to the value of the token.  This token will expire after 1 week.  The client should get a new token when this happens.

The `hashkey` is the unique identifier for the user, and should be saved, as it is needed in certain API requests.  If you have a valid token, you can get a hashkey later with the `auth_check` endpoint (see below).

Login
===================================

Please register a user before this!  Passwords must be at least 6 characters long.

Send a GET request to `/api/v1/login` with `Content-Type` set to `application/json`.

You will receive similar output to the register request.

Then do a POST request with the `X-CSRF-Token` and `Content-Type` headers set.

.. code-block:: shell

    {
    "email": "test@realize.pe",
    "password": "test11"
    }


You will now get an authentication token:

.. code-block:: shell

    {
      "user": {
        "hashkey": "df3cf9ecb8e65b53e1b4c6492e70eff8",
        "id": "1",
        "token": "WyIxIiwiNmVjOGMwOWQxY2JmMmUwZDVkODFkZWI0ZjgxYjhiNzciXQ.Bf54QQ.3xKpx9C_5gskeu3vJx_ytkgXU6c"
      }
    }


Verify token
===========================================

If you want to check the validity of an auth token, you can POST to `/api/v1/auth_check` with the `token` parameter set to the token.  You will receive the authentication status and user hashkey.