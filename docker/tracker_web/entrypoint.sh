#!/bin/sh

echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

echo "Database started"

python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec gunicorn --bind 0.0.0.0:8000 --workers 3 taskboard.wsgi:application