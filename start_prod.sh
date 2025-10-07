#!/bin/bash

# Production startup script
echo "🚀 Starting production server..."

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start production server with Gunicorn
exec gunicorn CVProject.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100
