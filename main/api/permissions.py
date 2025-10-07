from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS

from ..models import CV


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_staff)


class IsCVChecker(BasePermission):
    """Authenticated users with checker role can only read CVs.
    For now we treat any authenticated user as a checker unless other roles apply.
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.method in SAFE_METHODS)


class IsCVOwnerOrReadOnly(BasePermission):
    """Owners can modify their own CVs; others read-only if authenticated."""

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        if isinstance(obj, CV):
            return bool(request.user and obj.owner_id == getattr(request.user, 'id', None))
        return False

    def has_permission(self, request, view) -> bool:
        # For list/create; restrict any access to authenticated users
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated)
