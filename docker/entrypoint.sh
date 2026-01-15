#!/bin/bash
set -e

echo "=== MC Castellazzo Entrypoint ==="

# Wait for database
echo "Waiting for database..."
while ! python -c "
import os
import psycopg
conn = psycopg.connect(
    host=os.environ.get('POSTGRES_HOST', 'db'),
    port=os.environ.get('POSTGRES_PORT', '5432'),
    user=os.environ.get('POSTGRES_USER', 'mccastellazzob'),
    password=os.environ.get('POSTGRES_PASSWORD', ''),
    dbname=os.environ.get('POSTGRES_DB', 'mccastellazzob')
)
conn.close()
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser if not exists..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('SUPERUSER_USERNAME', 'admin')
email = os.environ.get('SUPERUSER_EMAIL', 'admin@mccastellazzob.com')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created')
else:
    print(f'Superuser {username} already exists')
"
fi

echo "=== Starting application ==="
exec "$@"
