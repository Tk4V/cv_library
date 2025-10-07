"""
PDF generation tasks.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any
from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from main.models import CV
from celery_tasks.services.pdf_service import PDFService

# Set up logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, name='celery_tasks.tasks.pdf.generate_cv_pdf_task')
def generate_cv_pdf_task(self, cv_id: int) -> Dict[str, Any]:
    """
    Generate CV PDF and return as base64 string.
    
    Args:
        cv_id: CV ID to generate PDF for
        
    Returns:
        Dict with PDF data and metadata
    """
    logger.info(f"📄 Starting PDF generation task for CV ID: {cv_id}")
    
    try:
        cv = CV.objects.get(pk=cv_id)
        logger.info(f"📄 Found CV: {cv.firstname} {cv.lastname} (ID: {cv_id})")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting PDF generation...'}
        )
        logger.info("📄 Task state updated: Starting PDF generation...")
        
        # Render PDF
        logger.info("📄 Starting PDF rendering...")
        pdf_service = PDFService()
        pdf_bytes = pdf_service.render_to_pdf_bytes("main/cv_pdf.html", {"cv": cv})
        logger.info(f"📄 PDF rendered successfully, size: {len(pdf_bytes)} bytes")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'PDF generated, encoding...'}
        )
        logger.info("📄 Task state updated: PDF generated, encoding...")
        
        # Convert to base64
        logger.info("📄 Converting PDF to base64...")
        import base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        logger.info(f"📄 PDF converted to base64, length: {len(pdf_base64)} characters")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'PDF generation complete!'}
        )
        logger.info("📄 Task state updated: PDF generation complete!")
        
        result = {
            'status': 'success',
            'pdf_data': pdf_base64,
            'filename': f'cv_{cv_id}_{cv.firstname}_{cv.lastname}.pdf',
            'size': len(pdf_bytes)
        }
        logger.info(f"✅ PDF generation task completed successfully: {result['filename']}, size: {result['size']} bytes")
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
        logger.error(f"❌ PDF generation task failed: {error_msg}")
        logger.exception("Full exception details:")
        return {
            'status': 'error',
            'error': error_msg
        }


@shared_task(bind=True, name='celery_tasks.tasks.pdf.generate_cv_pdf_download_task')
def generate_cv_pdf_download_task(self, cv_id: int) -> Dict[str, Any]:
    """
    Generate CV PDF and save to media storage for download.
    
    Args:
        cv_id: CV ID to generate PDF for
        
    Returns:
        Dict with download URL and metadata
    """
    try:
        cv = CV.objects.get(pk=cv_id)
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting PDF generation...'}
        )
        
        # Render PDF
        pdf_service = PDFService()
        pdf_bytes = pdf_service.render_to_pdf_bytes("main/cv_pdf.html", {"cv": cv})
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'PDF generated, saving...'}
        )
        
        # Create downloads directory
        downloads_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f'cv_{cv_id}_{unique_id}.pdf'
        file_path = os.path.join(downloads_dir, filename)
        
        # Save PDF to media storage
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'PDF saved successfully!'}
        )
        
        # Generate download URL
        download_url = f"{settings.MEDIA_URL}downloads/{filename}"
        
        return {
            'status': 'success',
            'download_url': download_url,
            'filename': filename,
            'size': len(pdf_bytes),
            'file_path': file_path
        }
        
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
