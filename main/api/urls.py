from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CVViewSet, RequestLogViewSet

router = DefaultRouter()
router.register(r'cv', CVViewSet, basename='cv')
router.register(r'logs', RequestLogViewSet, basename='logs')

urlpatterns = [
    path('', include(router.urls)),
]
