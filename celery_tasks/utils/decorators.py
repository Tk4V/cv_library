"""
Celery task decorators.
"""
import functools
import logging
from typing import Callable, Any
from celery import Task

logger = logging.getLogger(__name__)


def retry_task(max_retries: int = 3, countdown: int = 60):
    """
    Decorator for retrying failed tasks.
    
    Args:
        max_retries: Maximum number of retries
        countdown: Seconds to wait before retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: Task, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as exc:
                logger.error(f"Task {self.name} failed: {exc}")
                
                if self.request.retries < max_retries:
                    logger.info(f"Retrying task {self.name} (attempt {self.request.retries + 1})")
                    raise self.retry(countdown=countdown, exc=exc)
                else:
                    logger.error(f"Task {self.name} failed after {max_retries} retries")
                    raise exc
        
        return wrapper
    return decorator


def log_task_progress(func: Callable) -> Callable:
    """
    Decorator for logging task progress.
    
    Args:
        func: Task function to wrap
    """
    @functools.wraps(func)
    def wrapper(self: Task, *args, **kwargs) -> Any:
        logger.info(f"Starting task {self.name} with args: {args}, kwargs: {kwargs}")
        
        try:
            result = func(self, *args, **kwargs)
            logger.info(f"Task {self.name} completed successfully")
            return result
        except Exception as exc:
            logger.error(f"Task {self.name} failed with error: {exc}")
            raise exc
    
    return wrapper
