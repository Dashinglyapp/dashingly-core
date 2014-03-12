General usage
------------------------------------------

There are a few different commands that run various parts of realize.

Run the webserver:

.. code-block:: shell

    python manage.py runserver


Run delayed tasks:

.. code-block:: shell

    celery -A app.celery worker --loglevel=debug -B

Sync the frontend files from the angular UI repo:

.. code-block:: shell
    python manage.py syncjs -p PATH_TO_REALIZE_ANGULAR_DIR

Create migrations (if you change core/database/models.py):

.. code-block:: shell

    alembic revision --autogenerate -m "MESSAGE HERE"

Run tests (simple):

.. code-block:: shell

    python manage.py test

Run tests (more control):

.. code-block:: shell

    nosetests --with-coverage --cover-package="core" --logging-level="INFO"

Make a user an admin:

.. code-block:: shell

    python manage.py makeadmin -u USER_EMAIL