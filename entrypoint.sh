#!/usr/bin/env bash
set -e

cd /app/hotel_booking

if [ "${RUN_SETUP:-true}" = "true" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  python manage.py create_superuser
fi

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

exec gunicorn hotel_booking.wsgi:application \
  --bind "0.0.0.0:${PORT:-${APP_PORT:-8000}}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${REQUEST_TIMEOUT:-120}" \
  --access-logfile - \
  --error-logfile -
