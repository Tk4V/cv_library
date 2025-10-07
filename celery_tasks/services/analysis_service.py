"""
Analysis service for handling CV analysis operations.
"""
from typing import Dict, Optional
from celery.result import AsyncResult
from django.contrib.sessions.models import Session
from .base_service import BaseService


class AnalysisService(BaseService):
    """Service for handling CV analysis operations."""
    
    def __init__(self):
        super().__init__()
        self._task_module = 'celery_tasks.tasks.analysis'
        self._task_name = 'analyze_cv_task'
    
    def start_analysis(self, cv_id: int, question: str, session: Session) -> Dict[str, str]:
        """
        Start CV analysis task.
        
        Args:
            cv_id: CV ID to analyze
            question: Analysis question
            session: Django session object
            
        Returns:
            Dict with success status and task ID
        """
        if not question.strip():
            return {'error': 'Question is required'}
        
        if session.get('analysis_processing'):
            return {'error': 'Analysis already in progress'}
        
        try:
            task = self._get_task().delay(cv_id, question)
            self._store_task_info(session, task.id, question)
            return {'success': True, 'task_id': task.id}
        except Exception as e:
            return {'error': str(e)}
    
    def check_analysis_status(self, task_id: str, session: Session) -> Dict[str, str]:
        """
        Check analysis task status.
        
        Args:
            task_id: Celery task ID
            session: Django session object
            
        Returns:
            Dict with status and results
        """
        try:
            task_result = AsyncResult(task_id)
            
            if task_result.state == 'PENDING':
                return {'status': 'pending', 'message': 'Analysis in progress...'}
            elif task_result.state == 'SUCCESS':
                result = task_result.result
                self._store_completed_analysis(session, result)
                return {
                    'status': 'success',
                    'analysis': result['analysis'],
                    'question': result['question'],
                    'is_enabled': result['is_enabled']
                }
            else:
                self._clear_analysis_session(session)
                return {'status': 'error', 'message': 'Analysis failed'}
        except Exception as e:
            return {'error': str(e)}
    
    def clear_analysis(self, session: Session) -> Dict[str, str]:
        """
        Clear analysis state from session.
        
        Args:
            session: Django session object
            
        Returns:
            Dict with success status
        """
        self._clear_analysis_session(session)
        return {'success': True, 'message': 'Analysis state cleared'}
    
    def get_analysis_context(self, session: Session) -> Dict[str, any]:
        """
        Get analysis context for template rendering.
        
        Args:
            session: Django session object
            
        Returns:
            Dict with analysis context data
        """
        context = {
            'analysis_warning': '',
            'analysis_complete': None,
            'analysis_processing': False,
            'analysis_question': ''
        }
        
        # Check for completed analysis first
        analysis_complete = session.get('analysis_complete')
        if analysis_complete:
            context['analysis_complete'] = analysis_complete
        else:
            # Only check for pending tasks if no completed analysis
            analysis_task_id = session.get('analysis_task_id')
            if analysis_task_id:
                # Only check task status if we haven't checked in the last 2 seconds
                last_check = session.get('analysis_last_check', 0)
                import time
                current_time = time.time()
                
                if current_time - last_check > 2:  # 2 second cooldown
                    context.update(self._handle_pending_task(analysis_task_id, session))
                    session['analysis_last_check'] = current_time
                else:
                    # Use cached status
                    context.update({
                        'analysis_processing': True,
                        'analysis_question': session.get('analysis_question', '')
                    })
        
        # Check if analysis is enabled
        if not self.is_enabled():
            context['analysis_warning'] = 'CV analysis is not available. Please configure OpenAI API key.'
        
        return context
    
    def _handle_pending_task(self, task_id: str, session: Session) -> Dict[str, any]:
        """Handle pending analysis task."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Use AsyncResult with timeout to prevent blocking
            task_result = AsyncResult(task_id)
            
            # Try to get state with a very short timeout
            # If it takes too long, assume pending
            try:
                state = task_result.state
                logger.info(f"Task {task_id} state: {state}")
            except Exception as e:
                logger.error(f"Error getting task state: {e}")
                # If we can't get the state quickly, assume pending
                return {
                    'analysis_processing': True,
                    'analysis_question': session.get('analysis_question', '')
                }
            
            if state == 'SUCCESS':
                result = task_result.result
                analysis_data = {
                    'question': session.get('analysis_question', ''),
                    'analysis': result['analysis'],
                    'is_enabled': result['is_enabled']
                }
                # Store the completed analysis in session
                session['analysis_complete'] = analysis_data
                # Clear only the processing-related session data, keep the result
                session.pop('analysis_task_id', None)
                session.pop('analysis_processing', None)
                # Save the session to ensure it's persisted
                session.save()
                return {'analysis_complete': analysis_data}
            elif state == 'PENDING':
                return {
                    'analysis_processing': True,
                    'analysis_question': session.get('analysis_question', '')
                }
            elif state == 'PROGRESS':
                return {
                    'analysis_processing': True,
                    'analysis_question': session.get('analysis_question', '')
                }
            else:
                self._clear_analysis_session(session)
                return {'analysis_error': 'Analysis failed. Please try again.'}
        except Exception as e:
            # If there's any error checking the task, assume it's still pending
            # This prevents blocking the page load
            return {
                'analysis_processing': True,
                'analysis_question': session.get('analysis_question', '')
            }
    
    def _store_task_info(self, session: Session, task_id: str, question: str) -> None:
        """Store task information in session."""
        session['analysis_task_id'] = task_id
        session['analysis_question'] = question
        session['analysis_processing'] = True
        session.save()
    
    def _store_completed_analysis(self, session: Session, result: Dict) -> None:
        """Store completed analysis results in session."""
        session['analysis_complete'] = {
            'question': session.get('analysis_question', ''),
            'analysis': result['analysis'],
            'is_enabled': result['is_enabled']
        }
        # Clear only the processing-related session data, keep the result
        session.pop('analysis_task_id', None)
        session.pop('analysis_processing', None)
        session.save()
    
    def _clear_analysis_session(self, session: Session) -> None:
        """Clear analysis-related session data."""
        session.pop('analysis_task_id', None)
        session.pop('analysis_question', None)
        session.pop('analysis_processing', None)
        session.pop('analysis_complete', None)
        session.save()
