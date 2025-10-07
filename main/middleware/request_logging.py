from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import logging

from ..models import RequestLog

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            response = self.get_response(request)
        except Exception as exc:  # global catch to avoid raw 500s
            logger.exception("Unhandled exception at %s", request.path)
            # For API endpoints, let DRF handle; for UI, show friendly page
            if request.path.startswith('/api/'):
                raise
            return render(request, 'main/errors/500.html', status=500)
        try:
            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            remote_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
            RequestLog.objects.create(
                method=request.method,
                path=request.path,
                query_string=request.META.get('QUERY_STRING', ''),
                remote_ip=remote_ip or None,
                user=user,
            )
        except Exception:
            # Swallow logging errors to never break the main request
            logger.debug("Request logging failed for %s", request.path, exc_info=True)
        return response
