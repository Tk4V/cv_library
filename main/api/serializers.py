from rest_framework import serializers
from ..models import CV, RequestLog


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = [
            "id",
            "firstname",
            "lastname",
            "skills",
            "projects",
            "bio",
            "contacts",
        ]


class RequestLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = RequestLog
        fields = [
            "id",
            "timestamp",
            "method",
            "path",
            "query_string",
            "remote_ip",
            "username",
        ]
        read_only_fields = fields

    def get_username(self, obj):  # type: ignore[override]
        return obj.user.username if obj.user else None
