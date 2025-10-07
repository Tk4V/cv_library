"""
Cleanup tasks for maintenance.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from main.models import RequestLog


@shared_task(bind=True, name='celery_tasks.tasks.cleanup.cleanup_old_logs')
def cleanup_old_logs(self, days: int = 30) -> Dict[str, Any]:
    """
    Clean up old request logs.
    
    Args:
        days: Number of days to keep logs
        
    Returns:
        Dict with cleanup results
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Count logs before deletion
        old_logs_count = RequestLog.objects.filter(timestamp__lt=cutoff_date).count()
        
        # Delete old logs
        deleted_count, _ = RequestLog.objects.filter(timestamp__lt=cutoff_date).delete()
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
            'message': f'Cleaned up {deleted_count} old logs'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='celery_tasks.tasks.cleanup.cleanup_old_pdf_files')
def cleanup_old_pdf_files(self, days: int = 7) -> Dict[str, Any]:
    """
    Clean up old PDF files from media storage.
    
    Args:
        days: Number of days to keep PDF files
        
    Returns:
        Dict with cleanup results
    """
    try:
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdf')
        downloads_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
        
        deleted_files = []
        total_size = 0
        
        # Clean up PDF directory
        if os.path.exists(pdf_dir):
            cutoff_time = timezone.now() - timedelta(days=days)
            for filename in os.listdir(pdf_dir):
                file_path = os.path.join(pdf_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time.replace(tzinfo=timezone.utc) < cutoff_time:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append(filename)
                        total_size += file_size
        
        # Clean up downloads directory
        if os.path.exists(downloads_dir):
            cutoff_time = timezone.now() - timedelta(days=days)
            for filename in os.listdir(downloads_dir):
                file_path = os.path.join(downloads_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time.replace(tzinfo=timezone.utc) < cutoff_time:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append(filename)
                        total_size += file_size
        
        return {
            'status': 'success',
            'deleted_files': len(deleted_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'message': f'Cleaned up {len(deleted_files)} old PDF files'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='celery_tasks.tasks.cleanup.cleanup_orphaned_files')
def cleanup_orphaned_files(self) -> Dict[str, Any]:
    """
    Clean up orphaned files that are not referenced in the database.
    
    Returns:
        Dict with cleanup results
    """
    try:
        # This is a placeholder for more complex cleanup logic
        # In a real implementation, you would check file references in the database
        
        return {
            'status': 'success',
            'message': 'Orphaned files cleanup completed (placeholder)'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
