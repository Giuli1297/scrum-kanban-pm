#!/bin/bash
echo "INSTALACION"
sudo apt-get install -y virtualenv
echo "CREACION"
virtualenv --python=python3 is2_env

echo "\n\n\nACTIVACION\n\n\n"
source ./is2_env/bin/activate
pip list
pip install -r requirements.txt
suo -u postgres psql -c '\x' -c "CREATE DATABASE pmsdb;"
sudo -u postgres psql -c '\x' -c "ALTER USER postgres WITH PASSWORD 'postgres';"