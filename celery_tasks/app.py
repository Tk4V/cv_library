"""
Main Celery application configuration.
"""
import os
import django
from celery import Celery
from celery.signals import worker_ready

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVProject.settings.dev')

# Initialize Django
django.setup()

# Create Celery app
app = Celery('cv_project')

# Configure Celery
app.config_from_object('celery_tasks.config.settings')

# Auto-discover tasks
app.autodiscover_tasks([
    'celery_tasks.tasks.pdf',
    'celery_tasks.tasks.email', 
    'celery_tasks.tasks.analysis',
    'celery_tasks.tasks.notification',
    'celery_tasks.tasks.cleanup',
    'celery_tasks.tasks.statistics',
])

@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Signal handler for when worker is ready."""
    print("🚀 Celery worker is ready!")


if __name__ == '__main__':
    app.start()
