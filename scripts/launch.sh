#!/bin/bash
echo "INSTALACION"
sudo apt-get install -y virtualenv
echo "CREACION"
virtualenv --python=python3 venv

echo "\n\n\nACTIVACION\n\n\n"
source ./venv/bin/activate
pip list
pip install -r requirements.txt
sudo -u postgres psql -c '\x' -c "DROP DATABASE pmsdb;"
sudo -u postgres psql -c '\x' -c "CREATE DATABASE pmsdb;"
sudo -u postgres psql -c '\x' -c "ALTER USER postgres WITH PASSWORD 'postgres';"