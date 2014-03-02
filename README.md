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
