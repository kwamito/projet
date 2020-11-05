from rest_framework import serializers
from .models import Project
from users.models import Contributor
from users.serializers import ContributorSerializer


class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.ReadOnlyField(source="user.email")
    contributors = ContributorSerializer(many=True, read_only=False, required=False)
    contributors_count = serializers.ReadOnlyField(source="count_contributors")

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
            "contributors",
            "contributors_count",
        )
