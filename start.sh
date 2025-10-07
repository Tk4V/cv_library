#!/bin/bash

# Development startup script
echo "🔧 Starting development server..."

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver 0.0.0.0:8000
