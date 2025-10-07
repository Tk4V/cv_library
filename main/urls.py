from django.urls import include, path

urlpatterns = [
    path('', include('main.web.urls')),
    path('api/', include('main.api.urls')),
]

