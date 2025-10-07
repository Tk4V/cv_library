#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting CV Project entrypoint..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
python manage.py wait_for_db

# Run migrations only if not skipped
if [ "$SKIP_MIGRATIONS" != "1" ]; then
    echo "📊 Running database migrations..."
    python manage.py migrate --fake-initial
else
    echo "⏭️ Skipping migrations (SKIP_MIGRATIONS=1)"
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Clean up any problematic Silk profile files
echo "🧹 Cleaning up Silk profile files..."
find /app/media -name "*.prof" -type f -delete 2>/dev/null || true

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️ Superuser already exists')
"

# Load sample CV data
echo "📄 Loading sample CV data..."
python manage.py loaddata main/fixtures/sample_cvs.json

echo "✅ Entrypoint completed successfully!"

# Execute the main command
exec "$@"
