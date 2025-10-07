import logging
from django.contrib.auth import get_user

logger = logging.getLogger(__name__)

class AuthDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log authentication status
        user = get_user(request)
        session_key = request.session.session_key
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"User {request.user.username} is authenticated (session: {session_key})")
        else:
            logger.info(f"User is not authenticated (session: {session_key})")
        
        response = self.get_response(request)
        
        # Log session changes after request
        new_session_key = request.session.session_key
        if session_key != new_session_key:
            logger.info(f"Session changed from {session_key} to {new_session_key}")
        
        return response
