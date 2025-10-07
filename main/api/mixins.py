from __future__ import annotations


from rest_framework.request import Request

from ..common.time import filter_queryset_by_time


class TimeFilterMixin:
    """Reusable mixin to add since/until/preset/order filtering to a ViewSet.

    Set `time_filter_field` to the datetime field name on the model/queryset.
    """

    time_filter_field: str = "timestamp"

    def get_queryset(self):  # type: ignore[override]
        base_qs = super().get_queryset()  # type: ignore[misc]
        request: Request = self.request  # type: ignore[attr-defined]
        params = request.query_params
        return filter_queryset_by_time(
            base_qs,
            field=self.time_filter_field,
            since=params.get("since"),
            until=params.get("until"),
            preset=params.get("preset"),
            order=params.get("order"),
        )




