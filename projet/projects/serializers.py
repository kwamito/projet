from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Project
        fields = (
            "manager",
            "title",
            "is_public",
            "description",
            "created",
            "due_date",
            "priority",
            "documentation",
            "icon",
        )
