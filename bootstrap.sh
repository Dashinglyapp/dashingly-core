#!/usr/bin/env bash

apt-get install python-software-properties g++ make -y
add-apt-repository ppa:chris-lea/node.js -y
apt-get update -y
apt-get install nodejs -y
npm -g -y install grunt-cli karma bower
apt-get install build-essential -y

cd /vagrant
xargs -a apt-packages.txt apt-get install -y
pip install virtualenvwrapper
pip install -r requirements.txt
cd /realize-ui-angular
npm install -y
bower install -y
grunt dev