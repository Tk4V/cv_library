from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

from ..models import RequestLog
from ..common.time import filter_queryset_by_time


def filter_logs(queryset: QuerySet[RequestLog], since: Optional[str], until: Optional[str], preset: Optional[str], order: Optional[str]) -> QuerySet[RequestLog]:
    return filter_queryset_by_time(queryset, field='timestamp', since=since, until=until, preset=preset, order=order)
