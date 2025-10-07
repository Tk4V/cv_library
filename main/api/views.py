from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..enums import TimePreset, TimeOrder

from ..models import CV, RequestLog
from .serializers import CVSerializer, RequestLogSerializer
from .pagination import SmallResultsSetPagination
from ..filters.log_filters import filter_logs
from .mixins import TimeFilterMixin
from .permissions import IsAdmin, IsCVOwnerOrReadOnly, IsCVChecker


class CVViewSet(viewsets.ModelViewSet):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAdmin | IsCVOwnerOrReadOnly | IsCVChecker]

    def perform_create(self, serializer):
        serializer.save(owner=getattr(self.request, 'user', None))


class RequestLogViewSet(TimeFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    pagination_class = SmallResultsSetPagination
    time_filter_field = "timestamp"

    def get_queryset(self):
        qs = super().get_queryset()
        since = self.request.query_params.get('since')
        until = self.request.query_params.get('until')
        preset = self.request.query_params.get('preset')
        order = self.request.query_params.get('order')
        return filter_logs(qs, since, until, preset, order)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='since',
                description='Filter logs from this ISO 8601 timestamp (e.g. 2025-09-30T00:00:00Z)',
                required=False,
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='until',
                description='Filter logs up to this ISO 8601 timestamp (e.g. 2025-09-30T23:59:59Z)',
                required=False,
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='preset',
                description='Quick ranges',
                required=False,
                type={'type': 'string', 'enum': [TimePreset.LAST_HOUR, TimePreset.LAST_24H, TimePreset.LAST_WEEK, TimePreset.LAST_MONTH]},
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='order',
                description='Sort by timestamp',
                required=False,
                type={'type': 'string', 'enum': [TimeOrder.ASC, TimeOrder.DESC]},
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)










