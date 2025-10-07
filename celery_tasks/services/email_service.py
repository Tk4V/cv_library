"""
Email service for handling email operations.
"""
from typing import Dict, Optional
from django.contrib.sessions.models import Session
from .base_service import BaseService


class EmailService(BaseService):
    """Service for handling email operations."""
    
    def __init__(self):
        super().__init__()
        self._task_module = 'celery_tasks.tasks.email'
        self._task_name = 'email_cv_pdf_task'
    
    def send_cv_pdf(self, cv_id: int, recipient: str) -> Dict[str, str]:
        """
        Send CV PDF via email.
        
        Args:
            cv_id: CV ID to send
            recipient: Email recipient
            
        Returns:
            Dict with success status
        """
        if not recipient or '@' not in recipient:
            return {'error': 'Valid email address is required'}
        
        try:
            task = self._get_task().delay(cv_id, recipient)
            return {'success': True, 'message': f'PDF will be sent to {recipient}'}
        except Exception as e:
            return {'error': str(e)}
    
    def send_notification(self, recipient: str, subject: str, message: str) -> Dict[str, str]:
        """
        Send notification email.
        
        Args:
            recipient: Email recipient
            subject: Email subject
            message: Email message
            
        Returns:
            Dict with success status
        """
        try:
            from ..tasks.email import send_notification_email
            task = send_notification_email.delay(recipient, subject, message)
            return {'success': True, 'message': 'Notification sent'}
        except Exception as e:
            return {'error': str(e)}





