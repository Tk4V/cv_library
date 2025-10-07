"""
Email sending tasks.
"""
import logging
from typing import Dict, Any
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from main.models import CV

# Set up logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, name='celery_tasks.tasks.email.email_cv_pdf_task')
def email_cv_pdf_task(self, cv_id: int, recipient: str) -> Dict[str, Any]:
    """
    Send CV PDF via email.
    
    Args:
        cv_id: CV ID to send
        recipient: Email recipient
        
    Returns:
        Dict with success status
    """
    logger.info(f"📧 Starting email task for CV ID: {cv_id}, recipient: {recipient}")
    
    try:
        # Log email configuration
        logger.info(f"📧 Email configuration:")
        logger.info(f"  - EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
        logger.info(f"  - EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        logger.info(f"  - EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
        logger.info(f"  - EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
        logger.info(f"  - DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
        logger.info(f"  - EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
        
        cv = CV.objects.get(pk=cv_id)
        logger.info(f"📄 Found CV: {cv.firstname} {cv.lastname} (ID: {cv_id})")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Preparing email...'}
        )
        logger.info("📧 Task state updated: Preparing email...")
        
        # Generate PDF (simplified for email)
        logger.info("📄 Starting PDF generation...")
        from celery_tasks.services.pdf_service import PDFService
        pdf_service = PDFService()
        pdf_bytes = pdf_service.render_to_pdf_bytes("main/cv_pdf.html", {"cv": cv})
        logger.info(f"📄 PDF generated successfully, size: {len(pdf_bytes)} bytes")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'PDF generated, sending email...'}
        )
        logger.info("📧 Task state updated: PDF generated, sending email...")
        
        # Prepare email content
        subject = f'CV: {cv.firstname} {cv.lastname}'
        message = f'Please find attached the CV for {cv.firstname} {cv.lastname}.'
        logger.info(f"📧 Email content prepared - Subject: {subject}")
        
        # Send email with PDF attachment
        logger.info("📧 Creating EmailMessage...")
        from django.core.mail import EmailMessage
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach(
            f'cv_{cv_id}_{cv.firstname}_{cv.lastname}.pdf',
            pdf_bytes,
            'application/pdf'
        )
        logger.info(f"📧 EmailMessage created, attempting to send to: {recipient}")
        
        # Send the email
        email.send()
        logger.info("✅ Email sent successfully!")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Email sent successfully!'}
        )
        logger.info("📧 Task state updated: Email sent successfully!")
        
        result = {
            'status': 'success',
            'message': f'CV sent to {recipient}',
            'recipient': recipient
        }
        logger.info(f"✅ Email task completed successfully: {result}")
        return result
        
    except CV.DoesNotExist:
        error_msg = f'CV with ID {cv_id} not found'
        logger.error(f"❌ CV not found: {error_msg}")
        return {
            'status': 'error',
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Email task failed with exception: {error_msg}")
        logger.exception("Full exception details:")
        return {
            'status': 'error',
            'error': error_msg
        }


@shared_task(bind=True, name='celery_tasks.tasks.email.send_notification_email')
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
    logger.info(f"📧 Starting notification email task - Recipient: {recipient}, Subject: {subject}")
    
    try:
        logger.info(f"📧 Sending notification email to: {recipient}")
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        result = {
            'status': 'success',
            'message': f'Notification sent to {recipient}'
        }
        logger.info(f"✅ Notification email sent successfully: {result}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Notification email failed: {error_msg}")
        logger.exception("Full exception details:")
        return {
            'status': 'error',
            'error': error_msg
        }


@shared_task(bind=True, name='celery_tasks.tasks.email.send_cv_created_notification')
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


@shared_task(bind=True, name='celery_tasks.tasks.email.send_cv_updated_notification')
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
