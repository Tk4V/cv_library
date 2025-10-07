"""
Celery tasks package.
"""
from .pdf import *
from .email import *
from .analysis import *
from .notification import *
from .cleanup import *
from .statistics import *

__all__ = [
    # PDF tasks
    'generate_cv_pdf_task',
    'generate_cv_pdf_download_task',
    
    # Email tasks
    'email_cv_pdf_task',
    'send_notification_email',
    'send_cv_created_notification',
    'send_cv_updated_notification',
    
    # Analysis tasks
    'analyze_cv_task',
    
    # Notification tasks
    'send_notification_email',
    'send_cv_created_notification', 
    'send_cv_updated_notification',
    
    # Cleanup tasks
    'cleanup_old_logs',
    'cleanup_old_pdf_files',
    'cleanup_orphaned_files',
    
    # Statistics tasks
    'generate_daily_stats',
    'generate_weekly_report',
]
