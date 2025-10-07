from django.db import models
from django.contrib.auth import get_user_model

class CV(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    skills = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    contacts = models.TextField(blank=True)
    owner = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name='cvs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lastname", "firstname"]

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"


class RequestLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=512)
    query_string = models.CharField(max_length=1024, blank=True)
    remote_ip = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.timestamp} {self.method} {self.path}"


