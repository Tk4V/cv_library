from django.contrib import admin
from .models import CV, RequestLog


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname")
    search_fields = ("firstname", "lastname", "skills", "projects")

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'method', 'path', 'user']
    list_filter = ['method', 'timestamp']
    search_fields = ['path', 'user__username']
