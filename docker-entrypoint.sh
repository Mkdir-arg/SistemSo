#!/bin/bash
set -e

echo "🚀 Iniciando NODO..."

# Ejecutar migraciones y setup
echo "📦 Ejecutando migraciones..."
python manage.py migrate --noinput

echo "📋 Creando programas iniciales..."
python manage.py crear_programas || echo "⚠️  Programas ya existen"

echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Setup completado. Iniciando Gunicorn..."

# Iniciar Gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class gevent \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50
