"""
Main Celery configuration for CV Project.
This file imports the centralized Celery app from the celery package.
"""
import os
import django

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CVProject.settings.dev")

# Configure Django
django.setup()

# Import the main Celery app from the celery_tasks package
from celery_tasks.app import app as celery_app

# Export the app for Django
app = celery_app

# This is kept for backward compatibility
# The actual configuration is now in celery/config/settings.py


