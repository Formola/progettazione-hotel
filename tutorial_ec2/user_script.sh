#!/bin/bash -xeu

apt update
apt install python3 -y
apt-get -y install python3-pip curl git
git clone https://gitlab.com/HarshCasper/flask-api-example.git
cd flask-api-example
pip3 install flask
python3 app.py
