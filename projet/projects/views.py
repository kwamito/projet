from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import User, Contributor
from .models import (
    Project,
    Feature,
    Budget,
    BudgetHistory,
    Expense,
    PersonalBudget,
    PersonalExpense,
)
from users.permissions import IsOwnerOrReadOnly
from .serializers import (
    ProjectSerializer,
    FeatureSerializer,
    BudgetSerializer,
    BudgetHistorySerializer,
    ExpenseSerializer,
    PersonalBudgetSerializer,
    PersonalExpenseSerializer,
)
from rest_framework import status
from users.serializers import ContributorSerializer
from users.permissions import IsOwnerOrAdminOfProject, IsOwnerOrReadOnly
import json
from django.utils import timezone
from django.core.exceptions import ValidationError, SuspiciousOperation
from projects.custom_permissions import TestIfContributor, IsContributorOrDeny
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from django.db.models import Q

# Create your views here.
class ProjectCreateAPI(generics.ListCreateAPIView):
    queryset = Project.objects.filter(is_public=True)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UsersProjectsList(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class ProjectDetailUpdateDelete(APIView):
    def get(self, request, pk):
        project = Project.objects.get(id=pk)
        test = TestIfContributor(user=request.user, project_id=project.id)
        if test.test_is_contributor_or_manager() == True:
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        error = "You are not a contributor to this project"
        return Response(error, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, pk):
        project = Project.objects.get(id=pk)
        if request.user == project.user:
            project.delete()
            message = f"{project.title} has been deleted."
            return Response(message, status=status.HTTP_200_OK)
        else:
            return Response(
                "You are not the owner of this project",
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def patch(self, request, pk):
        project = Project.objects.get(id=pk)
        if request.user == project.user:
            seriailizer = ProjectSerializer(project, data=request.data)
            if seriailizer.is_valid():
                seriailizer.save()
                return Response(seriailizer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                "You are not the owner of this project",
                status=status.HTTP_401_UNAUTHORIZED,
            )


class AcceptContributor(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOfProject, IsOwnerOrReadOnly]
    queryset = Contributor.objects.all()

    def perform_update(self, serializer):
        serializer.save(accepted_by=self.request.user, date_accepted=timezone.now())

    def patch(self, request, project_id=None):
        contribution = self.request.user.contributions.get(project__id=project_id)
        contribution.accepted = True
        contribution.date_accepted = timezone.now()
        contribution.save()
        return Response("accepted", status=status.HTTP_202_ACCEPTED)


@api_view(["GET", "POST", "PATCH"])
def get_projects_contributors(request, project_id):
    if request.method == "GET":
        contributors = Contributor.objects.filter(project__id=project_id)
        serializer = ContributorSerializer(contributors, allow_null=True, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_project_pending_contributors(request, project_id, statum):
    if request.method == "GET":
        if statum == "pending":
            pending_contributors = Contributor.objects.filter(
                project__id=project_id, accepted=False
            )
            serializer = ContributorSerializer(pending_contributors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif statum == "accepted":
            accepted_contributors = Contributor.objects.filter(
                project__id=project_id, accepted=True
            )
            serializer = ContributorSerializer(accepted_contributors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class CreateFeature(APIView):
    queryset = Feature.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)

        # Replaced repeated test of whether a user is a conributor with a reusable function that does so
        test = TestIfContributor(request.user, project)

        if test.test_is_contributor_or_manager() is not True:
            error = "You have to be an accepted contributor or the project manager before you can make contributions."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data

        data["project"] = str(project.id)
        data["contributor"] = str(request.user.id)

        serializer = FeatureSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error = "Could not save feature"
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        error = "Method not allowed"
        return Response(error, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get(self, request, project_id, format=None):
        features = Feature.objects.filter(project__id=project_id)
        serializer = FeatureSerializer(features, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class FeatureDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeatureSerializer
    permission_classes = [
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        return Feature.objects.filter(contributor=self.request.user)


@api_view(["DELETE"])
def delete_feature(request, feature_id=None):
    if request.method == "DELETE":
        try:

            feature = Feature.objects.get(id=feature_id)

            project = feature.project
            check_feature_owner = TestIfContributor(user=request.user, project=project)
            if (
                check_feature_owner.test_is_owner_of_feature_and_manager(feature)
                == True
            ):

                feature.delete()
                return Response(
                    f"{feature.name} has been deleted from {project.title}",
                    status=status.HTTP_200_OK,
                )

            error = "You have to be the owner of this feature or manager of this project before you can delete."
            return Response(error, status.HTTP_401_UNAUTHORIZED)
        except Feature.DoesNotExist:
            error = "Feature does not exist."
            return Response(error, status=status.HTTP_404_NOT_FOUND)


@api_view(["PATCH"])
def review_feature(request, feature_id, format=None):
    if request.method == "PATCH":
        try:
            feature = Feature.objects.get(id=feature_id)
            project = feature.project
            if request.user == project.user:
                feature.reviewed = True
                feature.reviewed_by = request.user
                feature.save()
                return Response(
                    f"{feature.name} has been reviewed and is awaiting approval.",
                    status=status.HTTP_202_ACCEPTED,
                )

            error = "You have to be the manager/owner of this project before you can review this feature."
            return Response(error, status.HTTP_401_UNAUTHORIZED)
        except Feature.DoesNotExist:
            error = "Feature does not exist. Might have been deleted."
            return Response(error, status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def approve_feature(request, feature_id, format=None):
    if request.method == "PATCH":
        try:
            feature = Feature.objects.get(id=feature_id)
            project = feature.project
            if request.user == project.user:
                if feature.reviewed != True:
                    error = "Review this feature first."
                    return Response(error, status=status.HTTP_406_NOT_ACCEPTABLE)
                feature.approved = True
                feature.save()
                return Response(
                    f"{feature.name} has been approved.",
                    status=status.HTTP_202_ACCEPTED,
                )

            error = "You have to be the manager/owner of this project before you can approve it."
            return Response(error, status.HTTP_401_UNAUTHORIZED)
        except Feature.DoesNotExist:
            error = "Feature does not exist. Might have been deleted."
            return Response(error, status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def merge_features_documentation(request, feature_id):
    if request.method == "PATCH":
        try:
            feature = Feature.objects.get(id=feature_id)
            project = feature.project
            if request.user == project.user:
                if feature.approved != True:
                    error = "Approve this feature first."
                    return Response(error, status=status.HTTP_406_NOT_ACCEPTABLE)

                if project.documentation == None:
                    project.documentation = feature.documentation
                else:
                    project.documentation = (
                        project.documentation + "\n" + feature.documentation
                    )
                project.save()
                feature.merged = True
                feature.date_merged = timezone.now()
                feature.save()
                return Response(
                    f"{feature.name} has been merged.",
                    status=status.HTTP_202_ACCEPTED,
                )

            error = "You have to be the manager/owner of this project before you can merge it."
            return Response(error, status.HTTP_401_UNAUTHORIZED)
        except Feature.DoesNotExist:
            error = "Feature does not exist. Might have been deleted."
            return Response(error, status.HTTP_400_BAD_REQUEST)


class CreateRetrieveUpdateDeleteBudget(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def post(self, request, project_id=None, format=None):

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            error = "Project does not exist."
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        try:
            budget = Budget.objects.get(project=project)
            error = "You already have a budget for this project. You can update it."
            return Response(error, status=status.HTTP_208_ALREADY_REPORTED)
        except Budget.DoesNotExist:
            if request.user != project.user:
                error = "Only a manager can make a budget for the application."
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)
            serializer = BudgetSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                error = "Unknown error"
                return Response(error, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, project_id, format=None):
        budget = Budget.objects.get(project__id=project_id)
        serializer = BudgetSerializer(budget)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id, fromat=None):
        budget = Budget.objects.get(project__id=project_id)
        serializer = BudgetSerializer(budget, data=request.data)
        if request.user != budget.project.user:
            error = "Only project managers/owners can update budget info."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            from_amount = budget.amount
            to_amount = request.data["amount"]
            new_history = BudgetHistory.objects.create(
                budget=budget, from_amount=from_amount, to_amount=to_amount
            )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        error = "Unknown error"
        return Response(error, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def history(request, project_id):
    if request.method == "GET":
        history = BudgetHistory.objects.filter(budget__project__id=project_id).order_by(
            "-date_updated"
        )
        serializer = BudgetHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response("error", status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
def budget_history(request, project_id, history_id=None):
    if request.method == "GET":
        history = BudgetHistory.objects.filter(budget__project__id=project_id).order_by(
            "-date_updated"
        )
        serializer = BudgetHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == "DELETE":
        if history_id:
            try:
                history = BudgetHistory.objects.get(
                    budget__project__id=project_id, id=history_id
                )
                history.delete()
                message = "History deleted."
                return Response(message, status=status.HTTP_200_OK)
            except BudgetHistory.DoesNotExist:
                error = "History not found."
                return Response(error, status=status.HTTP_404_NOT_FOUND)
    return Response("Unknown error.", status=status.HTTP_302_FOUND)


class CreateExpense(APIView):
    def post(self, request, project_id=None, format=None):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            error = "Project does not exist."
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        test = TestIfContributor(user=request.user, project=project)

        if test.test_is_contributor_or_manager() is not True:
            error = "You have to be an accepted contributor in order to work on this project."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        data["contributor"] = request.user.id
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error = "Unknown error"
            return Response(error, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET", "PATCH", "DELETE"])
def expense_detail_update_delete(request, project_id, expense_id):
    if request.method == "GET":
        if expense_id:
            expense = Expense.objects.get(project__id=project_id, id=expense_id)
            serializer = ExpenseSerializer(expense)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            expenses = Expense.objects.filter(project__id=project_id)
            serializer = ExpenseSerializer(expenses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "PATCH":
        expense = Expense.objects.get(project__id=project_id, id=expense_id)
        project = Project.objects.get(id=project_id)
        if request.user == expense.contributor or request.user == project.user:
            serializer = ExpenseSerializer(expense, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        else:
            error = "Unauthorized update.You have to either be the spender or the project manager."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "DELETE":
        expense = Expense.objects.get(project__id=project_id, id=expense_id)
        project = Project.objects.get(id=project_id)
        if request.user == expense.contributor or request.user == project.user:
            expense.delete()
            message = "Expense has been deleted."
            return Response(message, status=status.HTTP_200_OK)
        else:
            error = "Only managers and spenders can delete expenses."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)
    error = "Method not allowed"
    return Response(error, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET", "POST"])
def create_personal_budget(request):
    if request.method == "POST":
        data = request.data
        data["user"] = request.user.id
        serializer = PersonalBudgetSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error = "Some error"
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response("Unknown error", status=status.HTTP_302_FOUND)


@api_view(["DELETE", "GET", "PATCH"])
def update_get_delete_personal_budget(request, budget_id):
    if request.method == "PATCH":
        budget = PersonalBudget.objects.get(id=budget_id, user=request.user)
        request.data["user"] = request.user.id
        serializer = PersonalBudgetSerializer(budget, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            error = "error"
            return Response(error, status=status.HTTP_403_FORBIDDEN)

    if request.method == "DELETE":
        budget = PersonalBudget.objects.get(id=budget_id, user=request.user)
        if request.user == budget.user:
            budget.delete()
            message = "Deleted"
            return Response(message, status=status.HTTP_200_OK)

        else:
            return Response("Unkown error", status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        budget = PersonalBudget.objects.get(id=budget_id, user=request.user)
        serializer = PersonalBudgetSerializer(budget)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def list_users_personal_budgets(request):
    budget = PersonalBudget.objects.filter(user=request.user).order_by("-date_created")
    if budget.exists() != True:
        message = "You have no budgets yet. You can create them."
    else:
        serializer = PersonalBudgetSerializer(budget, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_personal_expense(request, budget_id):
    if request.method == "POST":
        budget = PersonalBudget.objects.get(id=budget_id)
        serializer = PersonalExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(budget=budget)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error = "Unknown error"
            return Response(error, status=status.HTTP_201_CREATED)


@api_view(["DELETE", "GET", "PATCH"])
def get_delete_update_expenses(request, expense_id):
    expense = PersonalExpense.objects.get(id=expense_id)
    if request.method == "PATCH":

        if expense.budget.user == request.user:
            serializer = PersonalExpenseSerializer(expense, data=request.data)
            serializer.save()
        else:
            error = "You do not own this expense"
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        serializer = PersonalExpenseSerializer(expense)
        if request.user == expense.budget.user:
            return Response(serializer.data, status=status.HTTP_200_OK)
        error = "You do not own this expense."
        return Response(error, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "DELETE":
        if request.user == expense.budget.user:
            expense.delete()
            message = f"You have deleted {expense.name}"
            return Response(message, status=status.HTTP_200_OK)
        else:
            error = "You cannot delete someone else's expense."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def list_expenses_by_budget(request, budget_id):
    expenses = PersonalExpense.objects.filter(
        budget__id=budget_id, budget__user=request.user.id
    )
    if expenses.exists() is not True:
        raise NotFound(detail="This budget doesn't have any expenses yet.")
    seriailizer = PersonalExpenseSerializer(expenses, many=True)
    return Response(seriailizer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all_personal_expenses(request):
    expenses = PersonalExpense.objects.filter(budget__user=request.user)
    if expenses.exists() is not True:
        raise NotFound(detail="You don't have any expenses yet")
    serializer = PersonalExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
