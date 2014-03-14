#!/usr/bin/env bash

apt-get update -y
apt-get install build-essential -y
cd /vagrant
xargs -a apt-packages.txt apt-get install -y

npm config set registry http://registry.npmjs.org/
npm install -g n
n stable
npm -g install grunt-cli karma bower

pip install -r requirements.txt
python manage.py syncdb

service realize start
service celery start

