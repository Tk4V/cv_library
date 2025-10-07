"""
URL configuration for CVProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def health_check(request):
    return JsonResponse({"status": "healthy", "message": "CV Project is running"})

def db_health_check(request):
    import os
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        return JsonResponse({
            "status": "healthy", 
            "message": "Database is working",
            "database": connection.settings_dict['ENGINE'],
            "database_host": connection.settings_dict.get('HOST', 'N/A'),
            "database_name": connection.settings_dict.get('NAME', 'N/A'),
            "env_database_url": os.environ.get('DATABASE_URL', 'NOT_SET'),
            "env_keys": [k for k in os.environ.keys() if 'DATABASE' in k or 'DB' in k]
        })
    except Exception as e:
        return JsonResponse({
            "status": "error", 
            "message": f"Database error: {str(e)}",
            "env_database_url": os.environ.get('DATABASE_URL', 'NOT_SET'),
            "env_keys": [k for k in os.environ.keys() if 'DATABASE' in k or 'DB' in k]
        }, status=500)

def auth_debug(request):
    """Debug authentication and session status"""
    from django.contrib.sessions.models import Session
    from django.contrib.auth.models import User
    
    session_key = request.session.session_key
    is_authenticated = request.user.is_authenticated
    user_id = request.user.id if is_authenticated else None
    
    # Check if session exists in database
    session_exists = False
    if session_key:
        try:
            session_exists = Session.objects.filter(session_key=session_key).exists()
        except Exception as e:
            session_exists = f"Error: {str(e)}"
    
    return JsonResponse({
        "is_authenticated": is_authenticated,
        "user_id": user_id,
        "username": request.user.username if is_authenticated else None,
        "session_key": session_key,
        "session_exists_in_db": session_exists,
        "session_engine": request.session.__class__.__module__,
        "cookies": dict(request.COOKIES),
        "meta": {
            "REMOTE_ADDR": request.META.get('REMOTE_ADDR'),
            "HTTP_X_FORWARDED_FOR": request.META.get('HTTP_X_FORWARDED_FOR'),
            "HTTP_HOST": request.META.get('HTTP_HOST'),
        }
    })

def env_debug(request):
    """Debug environment variables"""
    import os
    from django.conf import settings
    
    # Get environment variables
    env_vars = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', 'NOT_SET'),
        'EMAIL_HOST_USER': os.environ.get('EMAIL_HOST_USER', 'NOT_SET'),
        'EMAIL_HOST_PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD', 'NOT_SET'),
        'POSTGRES_DB': os.environ.get('POSTGRES_DB', 'NOT_SET'),
        'POSTGRES_USER': os.environ.get('POSTGRES_USER', 'NOT_SET'),
        'POSTGRES_HOST': os.environ.get('POSTGRES_HOST', 'NOT_SET'),
        'DEBUG': os.environ.get('DEBUG', 'NOT_SET'),
        'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS', 'NOT_SET'),
    }
    
    # Get Django settings
    django_settings = {
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': settings.EMAIL_HOST,
    }
    
    return JsonResponse({
        "environment_variables": env_vars,
        "django_settings": django_settings,
        "all_env_keys": [k for k in os.environ.keys() if any(x in k for x in ['OPENAI', 'EMAIL', 'POSTGRES', 'DEBUG', 'ALLOWED'])]
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('health/', health_check, name='health_check'),
    path('db-health/', db_health_check, name='db_health_check'),
    path('auth-debug/', auth_debug, name='auth_debug'),
    path('env-debug/', env_debug, name='env_debug'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'main.web.error_views.bad_request'
handler403 = 'main.web.error_views.permission_denied'
handler404 = 'main.web.error_views.page_not_found'
handler500 = 'main.web.error_views.server_error'
