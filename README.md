Realize [![Build Status](https://travis-ci.org/realizeapp/realize-core.png?branch=master)](https://travis-ci.org/realizeapp/realize-core)
---------------------------------------

This is a minimal and work-in-progress version of [Realize](http://www.realize.pe).  Realize enables you to pull in and analyze data about your life.

Cross-platform quickstart
----------------------------------------

The easiest way to get started is with a Vagrant virtual machine:

First, [install VirtualBox](https://www.virtualbox.org/wiki/Downloads).

Next, [install Vagrant](http://www.vagrantup.com/downloads).

Then type:
```sh
git clone https://github.com/realizeapp/realize-core.git
cd realize-core
vagrant up
```

This should take 15-20 minutes to download and install dependencies on newer machines.

Once everything finishes, visiting `127.0.0.1:5000` in your browser will show a simple index page.  Please see the [documentation](http://realize-core.readthedocs.org/) for more information.

Full UI
---------------------------------------------

The full UI is in the `realize-ui-angular` repo.  In order to get it:

```sh
git clone https://github.com/realizeapp/realize-ui-angular.git
cd realize-core
python manage.py syncjs -p PATH_TO_REALIZE_ANGULAR_DIR
```

Visiting `127.0.0.1:5000` will now show you the realize UI instead of the index page.

Browsable API
---------------------------------------------

The easiest way to get started with the API is the browsable version.  Visit [http://127.0.0.1:5000/api/v1/spec.html#!/spec.json](http://127.0.0.1:5000/api/v1/spec.html#!/spec.json) to check it out.

Admin Dashboard
---------------------------------------------

An admin dashboard is available at `/admin`.  You can use it to edit and create different models, such as Users.  Only admins can access this dashboard.  See the documentation for how to make a user an admin.

Full Documentation
---------------------------------------------

Full documentation can be found at [http://realize-core.readthedocs.org](http://realize-core.readthedocs.org).

Contributions
--------------------------------------------

Contributions are very welcome.  If you want to contribute to the core, please fork and make a pull request.  We will review as soon as we can.  Plugins can and should be hosted in their own repositories.

Communication
--------------------------------------------

You can find us at #realize on freenode IRC.  You can also email us at <hello@realize.pe>.