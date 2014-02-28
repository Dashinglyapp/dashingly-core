This is a minimal and work-in-progress version of [Realize](http://www.realize.pe).

Get started with Vagrant
----------------------------------------

The easiest way to get started is with a Vagrant virtual machine:

```
Install vagrant (see this page -- http://www.vagrantup.com/downloads)
vagrant up
```

After running `vagrant up`, you will be able to ssh into the box and run the webserver:

```
vagrant ssh
cd /vagrant
python app.py
```

Opening up localhost:8080 in the browser on your machine will now show the webserver (vagrant forwards port 5000 from the virtual machine).  Vagrant keeps folders in sync, so editing things in the project folder will cause the changes to be mirrored and reloaded in Vagrant automatically.

If you want to run delayed tasks, open another ssh connection:

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
