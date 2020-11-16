from rest_framework import serializers
from .models import Project, Feature, Budget, BudgetHistory, Expense
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


class BudgetSerializer(serializers.ModelSerializer):
    date_created = serializers.ReadOnlyField()

    def update(self, instance, validated_data):
        instance.amount = validated_data.get("amount", instance.amount)
        instance.budget_type = validated_data.get("budget_type", instance.budget_type)
        instance.save()
        return instance

    class Meta:
        model = Budget
        fields = (
            "amount",
            "date_created",
            "budget_type",
            "id",
        )


class BudgetHistorySerializer(serializers.ModelSerializer):
    date_updated = serializers.ReadOnlyField()
    determine = serializers.ReadOnlyField()

    class Meta:
        model = BudgetHistory
        fields = (
            "from_amount_currency",
            "from_amount",
            "to_amount_currency",
            "to_amount",
            "date_updated",
            "budget",
            "determine",
            "id",
        )


class ExpenseSerializer(serializers.ModelSerializer):

    # contributor = serializers.ReadOnlyField(required=False)

    class Meta:
        model = Expense
        fields = ("amount", "description", "contributor", "date_expended")


class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.ReadOnlyField(source="user.email")
    contributors = ContributorSerializer(many=True, read_only=False, required=False)
    contributors_count = serializers.ReadOnlyField(source="count_contributors")
    features = FeatureSerializer(many=True, required=False)
    budget = BudgetSerializer(many=True, required=False)
    expense = ExpenseSerializer(required=False, many=True, read_only=False)
    spendings = ExpenseSerializer(many=True, required=False)

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
            "expense",
            "budget",
            "spendings",
            "total_expenditure",
            "over_budget_by",
            "over_budget_by_percentage",
        )
