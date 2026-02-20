#!/bin/bash
set -e

echo "Iniciando NODO..."

# Si Docker Compose/env provee un comando, delegar y salir.
# Esto permite que cada servicio (HTTP/WS) controle su propio flujo.
if [ "$#" -gt 0 ]; then
  echo "Comando personalizado detectado: $*"
  exec "$@"
fi

# Flujo por defecto (usado cuando no se pasa command)
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "Ejecutando migraciones..."
  python manage.py migrate --noinput
fi

if [ "${RUN_CREAR_SUPERADMIN:-false}" = "true" ]; then
  echo "Creando superadmin..."
  python manage.py crear_superadmin
fi

if [ "${RUN_CREAR_PROGRAMAS:-false}" = "true" ]; then
  echo "Creando programas iniciales..."
  python manage.py crear_programas || echo "Programas ya existen"
fi

if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
  echo "Recolectando archivos estaticos..."
  python manage.py collectstatic --noinput --clear
fi

echo "Setup completado. Iniciando Gunicorn..."
exec gunicorn --config gunicorn.conf.py config.wsgi:application