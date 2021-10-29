#!/bin/bash
echo "CREACION DEL ENTORNO VIRTUAL"
sudo apt-get install python3-venv
python3 -m venv env_desarrollo

echo "\n\n\nACTIVACION\n\n\n"
source ./env_desarrollo/bin/activate
pip install --upgrade pip
pip install -r ../requirements.txt

sudo -u postgres psql -c '\x' -c "DROP DATABASE IF EXISTS pmsdb;"
sudo -u postgres psql -c '\x' -c "CREATE DATABASE pmsdb;"
sudo -u postgres psql -c '\x' -c "ALTER USER postgres WITH PASSWORD 'postgres';"


echo "MIGRACIONES\n\n\n"
python ../manage.py makemigrations projectmanager
python ../manage.py migrate 

echo "CREACION DEL ADMINISTRADOR MAS CARGA DE BD\n\n\n"
python ../manage.py crear_admin
python ../manage.py runserver
