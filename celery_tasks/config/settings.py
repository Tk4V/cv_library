"""
Celery configuration settings.
"""
import os
from kombu import Queue

# Broker and result backend - prioritize REDIS_URL for DigitalOcean
redis_url = os.getenv('REDIS_URL', '')
if redis_url:
    # Ensure Redis URL has proper format with database number
    if not redis_url.endswith('/0') and not redis_url.endswith('/1'):
        redis_url = redis_url + '/0'
    broker_url = redis_url
    result_backend = redis_url
    print(f"DEBUG: Using Redis URL: {redis_url}")
    print(f"DEBUG: Broker URL: {broker_url}")
    print(f"DEBUG: Result backend: {result_backend}")
else:
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    print(f"DEBUG: Using fallback Redis URL: {broker_url}")

# Task serialization
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'

# Timezone
timezone = 'UTC'
enable_utc = True

# Task routing
task_routes = {
    'celery_tasks.tasks.pdf.*': {'queue': 'pdf_queue'},
    'celery_tasks.tasks.email.*': {'queue': 'email_queue'},
    'celery_tasks.tasks.analysis.*': {'queue': 'analysis_queue'},
    'celery_tasks.tasks.notification.*': {'queue': 'notification_queue'},
    'celery_tasks.tasks.cleanup.*': {'queue': 'cleanup_queue'},
    'celery_tasks.tasks.statistics.*': {'queue': 'statistics_queue'},
}

# Queue configuration
task_default_queue = 'default'
task_queues = (
    Queue('default', routing_key='default'),
    Queue('pdf_queue', routing_key='pdf'),
    Queue('email_queue', routing_key='email'),
    Queue('analysis_queue', routing_key='analysis'),
    Queue('notification_queue', routing_key='notification'),
    Queue('cleanup_queue', routing_key='cleanup'),
    Queue('statistics_queue', routing_key='statistics'),
)

# Task execution settings
task_acks_late = True
worker_prefetch_multiplier = 1
task_reject_on_worker_lost = True

# Task time limits
task_soft_time_limit = 300  # 5 minutes
task_time_limit = 600  # 10 minutes

# Result backend settings
result_expires = 3600  # 1 hour
result_persistent = True

# Worker settings
worker_max_tasks_per_child = 50
worker_disable_rate_limits = False

# Connection settings for production
broker_connection_retry_on_startup = True
broker_connection_retry = True
broker_connection_max_retries = 10

# Redis connection settings to prevent "Connection closed by server" errors
broker_pool_limit = 1  # Reduce pool size
broker_heartbeat = 60  # Increase heartbeat
broker_connection_timeout = 60  # Increase timeout
broker_connection_retry_delay = 2.0  # Increase retry delay

# Additional Redis settings for stability
broker_connection_retry = True
broker_connection_max_retries = 5
broker_connection_retry_on_startup = True

# Task result settings - using Redis backend
result_backend_transport_options = {
    'retry_policy': {
        'timeout': 5.0,
        'max_retries': 3,
    },
    'connection_pool_kwargs': {
        'max_connections': 10,
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {},
    }
}

# Logging
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Debug all environment variables
print("DEBUG: All environment variables:")
for key, value in os.environ.items():
    if 'REDIS' in key or 'CELERY' in key or 'PORT' in key:
        print(f"  {key}={value}")

print(f"DEBUG: Final broker_url: {broker_url}")
print(f"DEBUG: Final result_backend: {result_backend}")

# Beat schedule for periodic tasks
beat_schedule = {
    'cleanup-old-logs': {
        'task': 'celery_tasks.tasks.cleanup.cleanup_old_logs',
        'schedule': 86400.0,  # Daily
    },
    'cleanup-old-pdfs': {
        'task': 'celery_tasks.tasks.cleanup.cleanup_old_pdf_files',
        'schedule': 604800.0,  # Weekly
    },
    'generate-daily-stats': {
        'task': 'celery_tasks.tasks.statistics.generate_daily_stats',
        'schedule': 86400.0,  # Daily
    },
    'generate-weekly-report': {
        'task': 'celery_tasks.tasks.statistics.generate_weekly_report',
        'schedule': 604800.0,  # Weekly
    },
}
