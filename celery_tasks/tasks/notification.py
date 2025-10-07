"""
Notification tasks.
"""
from typing import Dict, Any
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from main.models import CV


@shared_task(bind=True, name='celery_tasks.tasks.notification.send_notification_email')
def send_notification_email(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
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
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        return {
            'status': 'success',
            'message': f'Notification sent to {recipient}'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='celery_tasks.tasks.notification.send_cv_created_notification')
def send_cv_created_notification(self, cv_id: int, user_email: str) -> Dict[str, Any]:
    """
    Send CV created notification.
    
    Args:
        cv_id: CV ID
        user_email: User email
        
    Returns:
        Dict with success status
    """
    try:
        cv = CV.objects.get(pk=cv_id)
        
        subject = 'CV Created Successfully'
        message = f'Your CV for {cv.firstname} {cv.lastname} has been created successfully.'
        
        return send_notification_email.delay(user_email, subject, message).get()
        
    except CV.DoesNotExist:
        return {
            'status': 'error',
            'error': f'CV with ID {cv_id} not found'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='celery_tasks.tasks.notification.send_cv_updated_notification')
def send_cv_updated_notification(self, cv_id: int, user_email: str) -> Dict[str, Any]:
    """
    Send CV updated notification.
    
    Args:
        cv_id: CV ID
        user_email: User email
        
    Returns:
        Dict with success status
    """
    try:
        cv = CV.objects.get(pk=cv_id)
        
        subject = 'CV Updated Successfully'
        message = f'Your CV for {cv.firstname} {cv.lastname} has been updated successfully.'
        
        return send_notification_email.delay(user_email, subject, message).get()
        
    except CV.DoesNotExist:
        return {
            'status': 'error',
            'error': f'CV with ID {cv_id} not found'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
