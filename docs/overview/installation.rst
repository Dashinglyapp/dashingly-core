Installation
--------------------------------

The easiest way to install Realize is to use Vagrant.  You can find quickstart instructions for vagrant in the `README.md <https://github.com/realizeapp/realize-core/blob/master/README.md>`_ file in the github repo.

Vagrant
================================

The easiest way to get started is with a Vagrant virtual machine:

First, `install VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.

Next, `install Vagrant <http://www.vagrantup.com/downloads>`_.

Then type:

.. code-block:: shell

    vagrant up

This should take 15-20 minutes to download and install dependencies on newer machines.

Then type:

.. code-block:: shell

    vagrant ssh
    cd /vagrant
    python manage.py runserver -hn 0.0.0.0

Vagrant forwards port 5000 in VirtualBox to `http://127.0.0.1:5000 <http://127.0.0.1:5000>`_ on your host machine, so you should be able to click the link and see the Realize UI.  Vagrant keeps folders in sync, so editing things in the project folder will cause the changes to be mirrored and reloaded in Vagrant automatically.

If you want to run delayed tasks (used for data import and analysis), open another ssh connection:

.. code-block:: shell

    vagrant ssh
    cd /vagrant
    celery -A app.celery worker --loglevel=debug -B

The frontend is not included with realize-core.  To get the frontend, clone the frontend repo, and run a management command to copy over the js:

.. code-block:: shell

    vagrant ssh
    cd /home/vagrant
    git clone https://github.com/realizeapp/realize-ui-angular.git
    cd /vagrant
    python manage.py syncjs -p /home/vagrant/realize-ui-angular


Visiting `http://127.0.0.1:5000 <http://127.0.0.1:5000>`_ will now show the AngularJS UI.  You will need to re-run the syncjs command whenever you update

Manual
============================================

You can also choose to do manual setup.  This is only really recommended for Linux, and has only been tested there.

Basic server setup:

.. code-block:: shell

    cd realize-core
    sudo xargs -a apt-packages.txt apt-get install
    pip install -r requirements.txt
    python manage.py syncdb

Frontend setup (needed for the realize UI):

.. code-block:: shell

    cd realize-core
    cd ..
    git clone https://github.com/realizeapp/realize-ui-angular.git
    cd realize-core
    python manage.py syncjs -p ../realize-ui-angular