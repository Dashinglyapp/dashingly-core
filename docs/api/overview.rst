API
--------------------------------

Realize-core exposes a full API that different frontends can connect to.  The easiest way to understand the API is to use our browable API feature.

Browsable API
============================================

To see the latest browsable API, visit `http://127.0.0.1:5000/api/v1/spec.html#!/spec.json <http://127.0.0.1:5000/api/v1/spec.html#!/spec.json>`_.  This will list all endpoints.  It is important to type in `127.0.0.1:500` instead of `localhost` because of cross-origin problems.

You will notice an `api_key` field in the top right.  If you have an authentication token, you can enter it here, otherwise scroll down a bit and click on `api/v1/register` or `api/v1/login`.  Type the needed information in and hit `submit`.  If it completes successfully, you will get a `token`, which you should copy and paste into the `api_key` field, and a `hashkey`, which you should note down, as it will be useful for requesting views specific to your user.

API Spec
============================================

Visit `api/v1/spec.json` to see the latest API spec file.

Fundamentals
============================================

The api takes data in JSON format, and returns JSON.

If there is an error with your request, it will return something that looks like this:

.. code-block:: shell

    {
        "code": 404,
        "error": true,
        "message": "404: Not Found"
    }

See `core.web.tests` for more details on how the flow works.

