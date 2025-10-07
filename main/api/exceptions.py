from __future__ import annotations

import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        # Standardize body shape
        data = {
            'detail': response.data.get('detail', 'Error'),
            'errors': response.data,
        }
        return Response(data, status=response.status_code, headers=response.headers)

    # Unhandled exceptions: log and return generic message
    request = context.get('request')
    path = getattr(request, 'path', '?')
    logger.exception("Unhandled API exception at %s", path)
    return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







