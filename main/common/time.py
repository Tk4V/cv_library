from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import QuerySet

from ..enums import TimePreset, TimeOrder


_PRESET_TO_DELTA = {
    TimePreset.LAST_HOUR: timedelta(hours=1),
    TimePreset.LAST_24H: timedelta(hours=24),
    TimePreset.LAST_WEEK: timedelta(days=7),
    TimePreset.LAST_MONTH: timedelta(days=30),
}


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    dt = parse_datetime(value)
    if not dt:
        return None
    if settings.USE_TZ and timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def current_time() -> datetime:
    return timezone.now() if settings.USE_TZ else datetime.now()


def preset_to_range(preset: Optional[str]) -> Optional[Tuple[datetime, datetime]]:
    if not preset:
        return None
    try:
        preset_enum = TimePreset(preset)
    except ValueError:
        return None
    now = current_time()
    since = now - _PRESET_TO_DELTA[preset_enum]
    return since, now


def filter_queryset_by_time(queryset: QuerySet, field: str, since: Optional[str], until: Optional[str], preset: Optional[str] = None, order: Optional[str] = None) -> QuerySet:
    since_dt = parse_iso_datetime(since)
    until_dt = parse_iso_datetime(until)
    if preset and not since_dt and not until_dt:
        range_tuple = preset_to_range(preset)
        if range_tuple:
            since_dt, until_dt = range_tuple
    if since_dt:
        queryset = queryset.filter(**{f"{field}__gte": since_dt})
    if until_dt:
        queryset = queryset.filter(**{f"{field}__lte": until_dt})
    try:
        order_enum = TimeOrder(order or 'desc')
    except ValueError:
        order_enum = TimeOrder.DESC
    if order_enum == TimeOrder.ASC:
        return queryset.order_by(field)
    return queryset.order_by(f"-{field}")
