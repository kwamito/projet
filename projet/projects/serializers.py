from rest_framework import serializers
from .models import Project, Feature
from users.models import Contributor
from users.serializers import ContributorSerializer


class FeatureSerializer(serializers.ModelSerializer):
    documentation = serializers.CharField(required=False)

    class Meta:
        model = Feature
        fields = (
            "contributor",
            "project",
            "name",
            "description",
            "date_created",
            "reviewed",
            "reviewed_by",
            "documentation",
            "date_reviewed",
            "merged",
            "date_merged",
            "cost",
            "due_date",
            "priority",
            "votes",
        )


class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.ReadOnlyField(source="user.email")
    contributors = ContributorSerializer(many=True, read_only=False, required=False)
    contributors_count = serializers.ReadOnlyField(source="count_contributors")
    features = FeatureSerializer(many=True)

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
            "features",
        )
