from rest_framework import serializers

from .models import Document, QueryLog


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document

        fields = [
            "id",
            "title",
            "content",
            "file",
            "uploaded_at",
            "owner",
        ]

        read_only_fields = [
            "id",
            "uploaded_at",
            "owner",
        ]


class QueryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryLog
        fields = [
            "id",
            "query_text",
            "result_summary",
            "created_at",
            "user",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "user",
        ]