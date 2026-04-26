#!/bin/sh
set -e

# DBの起動を待機
echo "Waiting for database..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
    print('Database is ready.')
except psycopg2.OperationalError:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done

# マイグレーション実行
echo "Running migrations..."
python manage.py migrate --no-input

# Gunicorn で起動
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --worker-class sync \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
