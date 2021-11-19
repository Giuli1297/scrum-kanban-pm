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
elif [ $ambiente = "2" ]
then
  git checkout desarrollo
fi
