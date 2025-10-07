"""
Template context processors for the CV Project.
"""
from django.conf import settings


def settings_context(request):
    """
    Inject Django settings into all templates.
    
    This context processor makes all Django settings available in templates
    as a 'settings' variable. Use with caution in production!
    """
    return {
        'settings': settings
    }







