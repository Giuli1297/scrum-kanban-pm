#!/bin/bash
echo "Deseas lanzar en:"
echo " (1) - Produccion"
echo " (2) - Desarrollo"
read ambiente
if [ $ambiente = "1" ]
then
  echo "Selecciona el tag: "
  echo " (1) - v0.1.0"
  echo " (2) - v0.2.0"
  echo " (3) - v0.3.0"
  echo " (4) - v0.4.0"
  echo " (5) - v0.5.0"
  echo " (6) - v1.0.0"
  read tag
  if [ $tag = "1" ]
  then
    git checkout v0.1.0
  elif [ $tag = "2" ]
  then
    git checkout v0.2.0
  elif [ $tag = "3" ]
  then
    git checkout v0.3.0
  elif [ $tag = "4" ]
  then
    git checkout v0.4.0
  elif [ $tag = "5" ]
  then
    git checkout v0.5.0
  elif [ $tag = "6" ]
  then
    git checkout v1.0.0
  fi

  echo "CREACION DEL ENTORNO VIRTUAL"
  sudo apt-get install python3-venv
  python3 -m venv env_desarrollo

  echo "\n\n\nACTIVACION\n\n\n"
  source ./env_desarrollo/bin/activate
  pip install --upgrade pip
  pip install -r ../requirements.txt


  psql -c "DATABASE IF EXISTS pmsdb;" -c "CREATE DATABASE pmsdb;" -U postgres


  echo "MIGRACIONES\n\n\n"
  python ../manage.py makemigrations projectmanager
  python ../manage.py migrate

  echo "CREACION DEL ADMINISTRADOR MAS CARGA DE BD\n\n\n"
  python ../manage.py createsuperuser
  python ../manage.py crear_admin
  python ../manage.py modify_site_prod
  if [ $tag = "6" ]
  then
    echo "Desea cargar datos de prueba?"
    echo " (1) - Si"
    echo " (2) - No"
    read choice1
    if [ $choice1 = "1" ]
    then
      python ../manage.py test_db_carga
    fi
  fi
  heroku pg:reset --confirm scrumkanbanpm
  git push heroku --force main
  PGUSER=postgres PGPASSWORD=postgres heroku pg:push pmsdb DATABASE_URL --app scrumkanbanpm
elif [ $ambiente = "2" ]
then
  git checkout desarrollo
  echo "CREACION DEL ENTORNO VIRTUAL"
  sudo apt-get install python3-venv
  python3 -m venv env_desarrollo

  echo "\n\n\nACTIVACION\n\n\n"
  source ./env_desarrollo/bin/activate
  pip install --upgrade pip
  pip install -r ../requirements.txt


  psql -c "DATABASE IF EXISTS pmsdb;" -c "CREATE DATABASE pmsdb;" -U postgres


  echo "MIGRACIONES\n\n\n"
  python ../manage.py makemigrations projectmanager
  python ../manage.py migrate

  echo "CREACION DEL ADMINISTRADOR MAS CARGA DE BD\n\n\n"
  python ../manage.py createsuperuser
  python ../manage.py crear_admin
  python ../manage.py modify_site_dev
  echo "Desea cargar datos de prueba?"
  echo " (1) - Si"
  echo " (2) - No"
  read choice1
  if [ $choice1 = "1" ]
  then
    python ../manage.py test_db_carga
  fi
  python ../manage.py runserver
fi
