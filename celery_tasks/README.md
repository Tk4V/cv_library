# Celery Task Management

This directory contains all Celery-related functionality for the CV Project, organized in a clean, structured way.

## Directory Structure

```
celery/
├── __init__.py              # Main package init
├── app.py                   # Celery application configuration
├── config/
│   ├── __init__.py
│   └── settings.py          # Celery configuration settings
├── tasks/
│   ├── __init__.py          # Task package init
│   ├── pdf.py              # PDF generation tasks
│   ├── email.py            # Email sending tasks
│   ├── analysis.py         # CV analysis tasks
│   ├── notification.py     # Notification tasks
│   ├── cleanup.py          # Maintenance tasks
│   └── statistics.py       # Statistics and reporting tasks
├── utils/
│   ├── __init__.py
│   ├── decorators.py       # Task decorators
│   └── helpers.py          # Helper functions
└── README.md               # This file
```

## Task Categories

### 1. PDF Tasks (`celery/tasks/pdf.py`)
- `generate_cv_pdf_task` - Generate CV PDF and return as base64
- `generate_cv_pdf_download_task` - Generate CV PDF and save for download

### 2. Email Tasks (`celery/tasks/email.py`)
- `email_cv_pdf_task` - Send CV PDF via email
- `send_notification_email` - Send general notification email
- `send_cv_created_notification` - Send CV created notification
- `send_cv_updated_notification` - Send CV updated notification

### 3. Analysis Tasks (`celery/tasks/analysis.py`)
- `analyze_cv_task` - Analyze CV content using AI

### 4. Notification Tasks (`celery/tasks/notification.py`)
- `send_notification_email` - Send notification email
- `send_cv_created_notification` - Send CV created notification
- `send_cv_updated_notification` - Send CV updated notification

### 5. Cleanup Tasks (`celery/tasks/cleanup.py`)
- `cleanup_old_logs` - Clean up old request logs
- `cleanup_old_pdf_files` - Clean up old PDF files
- `cleanup_orphaned_files` - Clean up orphaned files

### 6. Statistics Tasks (`celery/tasks/statistics.py`)
- `generate_daily_stats` - Generate daily statistics
- `generate_weekly_report` - Generate weekly statistics report

## Queue Configuration

Tasks are organized into different queues for better resource management:

- `default` - General tasks
- `pdf_queue` - PDF generation tasks
- `email_queue` - Email sending tasks
- `analysis_queue` - CV analysis tasks
- `notification_queue` - Notification tasks
- `cleanup_queue` - Maintenance tasks
- `statistics_queue` - Statistics tasks

## Running Celery

### Start All Workers
```bash
python manage.py run_celery_worker --worker-type all --concurrency 4
```

### Start Specific Worker
```bash
python manage.py run_celery_worker --worker-type pdf --concurrency 2
python manage.py run_celery_worker --worker-type email --concurrency 2
python manage.py run_celery_worker --worker-type analysis --concurrency 1
```

### Start Beat Scheduler
```bash
python manage.py run_celery_beat --loglevel info
```

### Start Flower (Monitoring)
```bash
celery -A CVProject flower
```

## Configuration

All Celery configuration is in `celery/config/settings.py`:

- **Broker**: Redis (configurable via `CELERY_BROKER_URL`)
- **Result Backend**: Redis (configurable via `CELERY_RESULT_BACKEND`)
- **Serialization**: JSON
- **Timezone**: UTC
- **Task Routing**: Queue-based routing
- **Beat Schedule**: Periodic tasks configuration

## Periodic Tasks

The following tasks run automatically:

- **Daily** (00:00 UTC):
  - `cleanup_old_logs` - Clean up logs older than 30 days
  - `generate_daily_stats` - Generate daily statistics

- **Weekly** (Monday 00:00 UTC):
  - `cleanup_old_pdf_files` - Clean up PDFs older than 7 days
  - `generate_weekly_report` - Generate weekly statistics

## Task Monitoring

### Using Flower
```bash
celery -A CVProject flower --port=5555
```
Access at: http://localhost:5555

### Using Celery CLI
```bash
# List active workers
celery -A CVProject inspect active

# List scheduled tasks
celery -A CVProject inspect scheduled

# List registered tasks
celery -A CVProject inspect registered
```

## Error Handling

All tasks include proper error handling and logging:

- **Retry Logic**: Configurable retry attempts
- **Progress Tracking**: Real-time progress updates
- **Error Logging**: Comprehensive error logging
- **Graceful Degradation**: Fallback behavior for failures

## Development

### Adding New Tasks

1. Create task in appropriate module in `celery/tasks/`
2. Add task name to `celery/tasks/__init__.py`
3. Update queue routing in `celery/config/settings.py` if needed
4. Test task execution

### Testing Tasks

```python
# Test task execution
from celery.tasks.pdf import generate_cv_pdf_task
result = generate_cv_pdf_task.delay(cv_id=1)
print(result.get())
```

## Production Deployment

### Docker Compose
```yaml
services:
  worker:
    build: .
    command: python manage.py run_celery_worker --worker-type all
    depends_on:
      - redis
      - db
  
  beat:
    build: .
    command: python manage.py run_celery_beat
    depends_on:
      - redis
      - db
```

### Supervisor Configuration
```ini
[program:celery-worker]
command=python manage.py run_celery_worker --worker-type all
directory=/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery-beat]
command=python manage.py run_celery_beat
directory=/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

## Best Practices

1. **Task Design**: Keep tasks small and focused
2. **Error Handling**: Always include proper error handling
3. **Logging**: Use structured logging for better debugging
4. **Monitoring**: Monitor task execution and performance
5. **Resource Management**: Use appropriate concurrency levels
6. **Queue Organization**: Group related tasks in same queue
7. **Testing**: Test tasks thoroughly before deployment
