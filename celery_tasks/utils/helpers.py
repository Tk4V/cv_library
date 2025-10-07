"""
Celery helper functions.
"""
import logging
from typing import Dict, Any, Optional
from celery import Task

logger = logging.getLogger(__name__)


def get_task_info(task: Task) -> Dict[str, Any]:
    """
    Get information about a task.
    
    Args:
        task: Celery task instance
        
    Returns:
        Dict with task information
    """
    return {
        'task_id': task.request.id,
        'task_name': task.name,
        'retries': task.request.retries,
        'max_retries': task.max_retries,
        'eta': task.request.eta,
        'expires': task.request.expires,
        'args': task.request.args,
        'kwargs': task.request.kwargs,
    }


def format_task_result(result: Any) -> Dict[str, Any]:
    """
    Format task result for logging.
    
    Args:
        result: Task result
        
    Returns:
        Formatted result dict
    """
    if isinstance(result, dict):
        return result
    elif isinstance(result, (str, int, float, bool)):
        return {'result': result}
    else:
        return {'result': str(result)}


def log_task_progress(task: Task, current: int, total: int, status: str) -> None:
    """
    Log task progress.
    
    Args:
        task: Celery task instance
        current: Current progress
        total: Total progress
        status: Status message
    """
    percentage = (current / total) * 100 if total > 0 else 0
    
    logger.info(
        f"Task {task.name} progress: {current}/{total} ({percentage:.1f}%) - {status}"
    )
    
    # Update task state
    task.update_state(
        state='PROGRESS',
        meta={
            'current': current,
            'total': total,
            'status': status,
            'percentage': percentage
        }
    )
