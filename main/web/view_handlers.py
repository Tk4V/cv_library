"""
View handlers for separating business logic from view classes.
"""
from typing import Dict, Any, Optional
from django.http import HttpRequest
from ..models import CV
from ..enums import Language
from ..services import TranslationService
from celery_tasks.services.analysis_service import AnalysisService
from celery_tasks.services.pdf_service import PDFService


class CVDetailHandler:
    """Handler for CV detail view operations."""
    
    def __init__(self):
        self.translation_service = TranslationService()
        self.analysis_service = AnalysisService()
        self.pdf_service = PDFService()
    
    def handle_email_request(self, request: HttpRequest, cv_id: int) -> Optional[Dict[str, str]]:
        """Handle email PDF request."""
        import logging
        logger = logging.getLogger(__name__)
        
        recipient = request.POST.get('email')
        logger.info(f"📧 Email request received - CV ID: {cv_id}, Recipient: {recipient}")
        
        if not recipient:
            logger.warning("❌ No email recipient provided")
            return {'error': 'Please enter a valid email address'}
        
        # Validate email format
        if '@' not in recipient or '.' not in recipient.split('@')[-1]:
            logger.warning(f"❌ Invalid email format: {recipient}")
            return {'error': 'Please enter a valid email address'}
        
        try:
            logger.info(f"📧 Queuing email task for CV {cv_id} to {recipient}")
            # Use async email task instead of synchronous
            from celery_tasks.tasks.email import email_cv_pdf_task
            task = email_cv_pdf_task.delay(cv_id, recipient)
            logger.info(f"✅ Email task queued successfully with ID: {task.id}")
            
            result = {
                'success': True,
                'message': f'PDF will be sent to {recipient} shortly. Check your email in a few moments.'
            }
            logger.info(f"✅ Email request handled successfully: {result}")
            return result
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Email request failed: {error_msg}")
            logger.exception("Full exception details:")
            
            # Check if it's a Redis connection error
            if "Connection closed by server" in error_msg or "redis" in error_msg.lower():
                logger.warning("🔄 Redis connection error detected, trying fallback...")
                try:
                    # Fallback: send email directly without Celery
                    result = self._send_email_directly(cv_id, recipient)
                    if result.get('status') == 'success':
                        logger.info("✅ Fallback email sending succeeded")
                        return {
                            'success': True,
                            'message': f'PDF sent to {recipient} successfully (fallback mode).'
                        }
                    else:
                        logger.error(f"❌ Fallback email sending failed: {result.get('error', 'Unknown error')}")
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback email sending also failed: {str(fallback_error)}")
            
            return {'error': f'Failed to send email: {error_msg}'}
    
    def handle_translation_request(self, request: HttpRequest, cv: CV) -> Optional[Dict[str, Any]]:
        """Handle translation request."""
        lang = request.POST.get('lang', '').strip()
        if not lang:
            return None
        
        try:
            lang_enum = Language(lang)
        except ValueError:
            return None
        
        translations, enabled = self.translation_service.translate_cv(cv, lang_enum.value)
        return {
            'lang': lang,
            'enabled': enabled,
            **translations
        }
    
    def handle_analysis_request(self, request: HttpRequest, cv_id: int) -> Optional[Dict[str, str]]:
        """Handle analysis request."""
        question = request.POST.get('analysis_question', '').strip()
        if not question:
            return {'error': 'Please enter a question'}
        
        return self.analysis_service.start_analysis(cv_id, question, request.session)
    
    def handle_clear_analysis_request(self, request: HttpRequest) -> Optional[Dict[str, str]]:
        """Handle clear analysis request."""
        return self.analysis_service.clear_analysis(request.session)
    
    def get_analysis_context(self, request: HttpRequest) -> Dict[str, Any]:
        """Get analysis context for template."""
        return self.analysis_service.get_analysis_context(request.session)
    
    def get_translation_context(self, request: HttpRequest) -> Dict[str, Any]:
        """Get translation context for template."""
        context_trans = request.session.pop('cv_translations', None)
        if not context_trans:
            return {}
        
        return {
            'translated': context_trans,
            'translation_warning': context_trans.get('warning', '') if not context_trans.get('enabled') else ''
        }
    
    def _send_email_directly(self, cv_id: int, recipient: str) -> Dict[str, Any]:
        """Send email directly without Celery (fallback method)."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from django.conf import settings
            from main.models import CV
            from celery_tasks.services.pdf_service import PDFService
            from django.core.mail import EmailMessage
            
            logger.info(f"📧 Fallback: Sending email directly for CV {cv_id} to {recipient}")
            
            # Get CV
            cv = CV.objects.get(pk=cv_id)
            logger.info(f"📄 Found CV: {cv.firstname} {cv.lastname}")
            
            # Generate PDF
            logger.info("📄 Generating PDF...")
            pdf_service = PDFService()
            pdf_bytes = pdf_service.render_to_pdf_bytes("main/cv_pdf.html", {"cv": cv})
            logger.info(f"📄 PDF generated, size: {len(pdf_bytes)} bytes")
            
            # Prepare email
            subject = f'CV: {cv.firstname} {cv.lastname}'
            message = f'Please find attached the CV for {cv.firstname} {cv.lastname}.'
            
            # Send email
            logger.info("📧 Sending email...")
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
            email.send()
            
            logger.info("✅ Fallback email sent successfully!")
            return {
                'status': 'success',
                'message': f'Email sent to {recipient}',
                'recipient': recipient
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback email failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }


