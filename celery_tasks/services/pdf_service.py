"""
PDF service for handling PDF generation operations.
"""
from typing import Dict, Optional
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from celery.result import AsyncResult
from django.contrib.sessions.models import Session
from .base_service import BaseService


class PDFService(BaseService):
    """Service for handling PDF generation operations."""
    
    def __init__(self):
        super().__init__()
        self._task_module = 'celery_tasks.tasks.pdf'
        self._task_name = 'generate_cv_pdf_download_task'
    
    def start_pdf_generation(self, cv_id: int, session: Session) -> Dict[str, str]:
        """
        Start PDF generation task.
        
        Args:
            cv_id: CV ID to generate PDF for
            session: Django session object
            
        Returns:
            Dict with success status and task ID
        """
        try:
            task = self._get_task().delay(cv_id)
            session['pdf_task_id'] = task.id
            return {'success': True, 'task_id': task.id}
        except Exception as e:
            return {'error': str(e)}
    
    def check_pdf_status(self, task_id: str) -> Dict[str, str]:
        """
        Check PDF generation status.
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Dict with status and download URL
        """
        try:
            task_result = AsyncResult(task_id)
            
            if task_result.state == 'SUCCESS':
                result = task_result.result
                return {
                    'status': 'success',
                    'download_url': result.get('download_url', '')
                }
            elif task_result.state == 'PENDING':
                return {'status': 'pending', 'message': 'PDF generation in progress...'}
            else:
                return {'status': 'error', 'message': 'PDF generation failed'}
        except Exception as e:
            return {'error': str(e)}
    
    def clear_pdf_session(self, session: Session) -> None:
        """Clear PDF-related session data."""
        session.pop('pdf_task_id', None)
    
    def generate_cv_pdf_download(self, cv_id: int) -> Dict[str, str]:
        """
        Generate CV PDF for immediate download.
        
        Args:
            cv_id: CV ID to generate PDF for
            
        Returns:
            Dict with download URL or error
        """
        try:
            from main.models import CV
            import os
            import uuid
            from pathlib import Path
            from django.conf import settings
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            # Get CV object
            cv = CV.objects.get(pk=cv_id)
            
            # Render PDF
            pdf_bytes = self.render_to_pdf_bytes("main/cv_pdf.html", {"cv": cv})
            
            # Create downloads directory
            downloads_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Generate unique filename
            unique_id = str(uuid.uuid4())[:8]
            filename = f"cv_{cv_id}_{unique_id}.pdf"
            file_path = os.path.join(downloads_dir, filename)
            
            # Save PDF to file
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            # Return download URL
            download_url = f"/media/downloads/{filename}"
            
            return {
                'success': True,
                'download_url': download_url,
                'filename': filename
            }
        except Exception as e:
            return {'error': str(e)}
    
    def render_to_pdf_bytes(self, template_name: str, context: dict) -> bytes:
        """
        Render a Django template to PDF bytes.
        
        Args:
            template_name: Name of the Django template
            context: Template context data
            
        Returns:
            PDF bytes
        """
        template = get_template(template_name)
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.CreatePDF(src=html, dest=result, encoding="utf-8")
        if pdf.err:
            raise ValueError("PDF generation error")
        return result.getvalue()
    
    def as_http_response(self, template_name: str, context: dict, filename: str) -> HttpResponse:
        """
        Create an HTTP response with PDF content.
        
        Args:
            template_name: Name of the Django template
            context: Template context data
            filename: Name for the downloaded file
            
        Returns:
            HttpResponse with PDF content
        """
        try:
            pdf_bytes = self.render_to_pdf_bytes(template_name, context)
        except ValueError:
            return HttpResponse("PDF generation error", status=500)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
