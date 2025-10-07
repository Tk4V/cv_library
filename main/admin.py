from django.contrib import admin
from .models import CV, RequestLog


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    """Enhanced CV Admin with better UI and functionality"""
    
    list_display = ('id', 'firstname', 'lastname', 'owner', 'created_at', 'updated_at')
    list_display_links = ('id', 'firstname', 'lastname')
    list_filter = ('created_at', 'updated_at', 'owner')
    search_fields = ('firstname', 'lastname', 'skills', 'projects', 'bio', 'contacts')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'firstname', 'lastname', 'owner')
        }),
        ('Professional Details', {
            'fields': ('bio', 'skills', 'projects')
        }),
        ('Contact Information', {
            'fields': ('contacts',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('owner')


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """Enhanced Request Log Admin with better filtering and display"""
    
    list_display = ('id', 'timestamp', 'method', 'path', 'user', 'remote_ip')
    list_display_links = ('id', 'timestamp')
    list_filter = ('method', 'timestamp', 'user')
    search_fields = ('path', 'query_string', 'user__username', 'remote_ip')
    readonly_fields = ('id', 'timestamp', 'method', 'path', 'query_string', 'remote_ip', 'user')
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    fieldsets = (
        ('Request Information', {
            'fields': ('id', 'timestamp', 'method', 'path', 'query_string')
        }),
        ('User Information', {
            'fields': ('user', 'remote_ip')
        }),
    )
    
    def has_add_permission(self, request):
        # Logs are created automatically, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Logs should not be edited
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
