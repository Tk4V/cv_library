from django.db.models import Q, QuerySet

from ..models import CV


def filter_cvs_by_query(queryset: QuerySet[CV], query: str) -> QuerySet[CV]:
    query = (query or "").strip()
    if not query:
        return queryset
    return queryset.filter(Q(firstname__icontains=query) | Q(lastname__icontains=query))

