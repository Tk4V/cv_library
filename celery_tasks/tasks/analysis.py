"""
CV analysis tasks.
"""
from typing import Dict, Any
from celery import shared_task
from django.conf import settings

from main.models import CV
from main.services import CVAnalysisService


@shared_task(bind=True, name='celery_tasks.tasks.analysis.analyze_cv_task')
def analyze_cv_task(self, cv_id: int, question: str) -> Dict[str, Any]:
    """
    Analyze CV content using AI.
    
    Args:
        cv_id: CV ID to analyze
        question: Analysis question
        
    Returns:
        Dict with analysis results
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting analysis for CV {cv_id} with question: {question}")
        cv = CV.objects.get(pk=cv_id)
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting analysis...'}
        )
        
        # Initialize analysis service
        analysis_service = CVAnalysisService()
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Analyzing CV content...'}
        )
        
        # Perform analysis
        logger.info("Calling analysis service...")
        analysis, is_enabled = analysis_service.analyze_cv(cv, question)
        logger.info(f"Analysis completed. Enabled: {is_enabled}, Analysis length: {len(analysis) if analysis else 0}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Processing analysis results...'}
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Analysis complete!'}
        )
        
        result = {
            'status': 'success',
            'analysis': analysis,
            'question': question,
            'is_enabled': is_enabled,
            'cv_id': cv_id
        }
        
        return result
        
    except CV.DoesNotExist:
        error_msg = f'CV with ID {cv_id} not found'
        logger.error(error_msg)
        return {
            'status': 'error',
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Analysis task failed: {error_msg}")
        return {
            'status': 'error',
            'error': error_msg
        }
