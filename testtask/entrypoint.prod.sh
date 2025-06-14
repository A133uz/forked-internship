#!/usr/bin/env bash

# Create staticfiles directory and set permissions if it doesn't exist
mkdir -p /app/staticfiles
chown -R appuser:appuser /app/staticfiles

# Switch to non-root user
su appuser -c "
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Run migrations
    python manage.py migrate
    
    # Start the application with Gunicorn
    python -m gunicorn --bind 0.0.0.0:8000 --workers 3 testtask.wsgi:application
"