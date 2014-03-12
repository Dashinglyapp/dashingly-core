Management Commands
---------------------------------------------

Management commands are run with `python manage.py COMMAND_NAME`.

Available commands:

* runserver -- runs the webserver.  Has option -p for port and -hn for hostname.
* syncdb -- Migrates the database to the newest version.
* syncjs -- Syncs javascript from the frontend to flask.
* makeadmin -- Makes a user an admin.
* test -- Runs tests for the project.
