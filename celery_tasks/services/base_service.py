"""
Base service class with common functionality.
"""
from typing import Any
from celery import shared_task


class BaseService:
    """Base service class with common functionality."""
    
    def __init__(self):
        self._task_module = None
        self._task_name = None
    
    def _get_task(self):
        """Get Celery task dynamically."""
        if not self._task_module or not self._task_name:
            raise ValueError("Task module and name must be set")
        
        module = __import__(self._task_module, fromlist=[self._task_name])
        return getattr(module, self._task_name)
    
    def is_enabled(self) -> bool:
        """Check if service is enabled."""
        return True





