from rest_framework import serializers
from .models import (
    Project,
    Feature,
    Budget,
    BudgetHistory,
    Expense,
    PersonalBudget,
    PersonalExpense,
    Task,
    Team,
)
from users.models import Contributor
from users.serializers import ContributorSerializer


class FeatureSerializer(serializers.ModelSerializer):
    documentation = serializers.CharField(required=False)
    profile_image = serializers.ImageField(
        required=False, source="contributor.profile.image"
    )

    class Meta:
        model = Feature
        fields = (
            "id",
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
            "time_since_created",
            "time_since_reviewed",
            "time_since_merged",
            "time_to_due_date",
            "profile_image",
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
        fields = (
            "amount",
            "description",
            "contributor",
            "date_expended",
            "contributor_email",
            "total_expenses",
        )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "start_date",
            "due_date",
            "date_created",
            "completed",
            "priority",
            "date_completed",
            "assignees",
            "theme",
            "assignees_names",
            "total_number_of_assignees",
            "time_to_due_date",
            "time_to_start_date",
        )


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = (
            "name",
            "contributors",
            "tasks",
            "date_created",
            "project",
            "contributors_names",
            "id",
        )


class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.ReadOnlyField(source="user.email")
    contributors = ContributorSerializer(many=True, read_only=False, required=False)
    contributors_count = serializers.ReadOnlyField(source="count_contributors")
    features = FeatureSerializer(many=True, required=False)
    budget = BudgetSerializer(many=True, required=False)
    expense = ExpenseSerializer(required=False, many=True, read_only=False)
    spendings = ExpenseSerializer(many=True, required=False)
    tasks = TaskSerializer(many=True, required=False)
    id = serializers.IntegerField(read_only=False, required=False)
    time_since_created = serializers.ReadOnlyField()
    tasks_completed = serializers.ReadOnlyField()
    teams = TeamSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = (
            "id",
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
            "tasks",
            "time_since_created",
            "tasks_completed",
            "tasks_done",
            "budget_percent",
            "budget_by_pure_number",
            "teams",
            "number_of_completed_tasks",
            "all_tasks_count",
            "all_uncompleted_tasks",
            "weeks_tasks",
        )


class PersonalBudgetSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = PersonalBudget
        fields = ("name", "description", "amount", "date_created")


class PersonalExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalExpense
        fields = ("name", "description", "amount", "date_created", "budget")


class ProjectDocumentationSerializer(serializers.Serializer):
    documentation = serializers.CharField(read_only=False)
