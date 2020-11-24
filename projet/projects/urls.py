from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from rest_framework.routers import Route, DynamicRoute, SimpleRouter
from rest_framework_extensions.routers import ExtendedSimpleRouter


urlpatterns = [
    path("create-list/", views.ProjectCreateAPI.as_view(), name="project-create"),
    path("my-projects/", views.UsersProjectsList.as_view(), name="users-projects"),
    path(
        "my-project/<int:pk>/",
        views.ProjectDetailUpdateDelete.as_view(),
        name="update-delete",
    ),
    path(
        "accept/<int:project_id>/<int:contributor_id>/",
        views.AcceptContributor.as_view(),
        name="accept-contribution",
    ),
    path(
        "contributors/<int:project_id>/",
        views.get_projects_contributors,
        name="contributors",
    ),
    path(
        "contributors/<int:project_id>/<str:statum>/",
        views.get_project_pending_contributors,
        name="pending-accepted-contributors",
    ),
    path("contribute/<int:project_id>/", views.contribute, name="contribute"),
    path(
        "approve-feature/<int:feature_id>/",
        views.approve_feature,
        name="approve-feature",
    ),
    path(
        "review-feature/<int:feature_id>/", views.review_feature, name="review-feature"
    ),
    path(
        "merge/<int:feature_id>/",
        views.merge_features_documentation,
        name="merge-feature",
    ),
    path(
        "budget-create/<int:project_id>/",
        views.CreateRetrieveUpdateDeleteBudget.as_view(),
        name="budget-create",
    ),
    path(
        "budget-history/<int:project_id>/<int:history_id>/",
        views.budget_history,
        name="budget-history",
    ),
    path(
        "expense-create/<int:project_id>/",
        views.CreateExpense.as_view(),
        name="expense-create",
    ),
    path(
        "expense/<int:project_id>/<int:expense_id>/",
        views.expense_detail_update_delete,
        name="expense-detail-delete",
    ),
    path("personal-budget/", views.create_personal_budget, name="personal-budget"),
    path(
        "update-budget/<int:budget_id>/",
        views.update_get_delete_personal_budget,
        name="something",
    ),
    path("all-personal/", views.list_users_personal_budgets),
    path("create-expense/<int:budget_id>/", views.create_personal_expense),
    path(
        "create-feature/<int:project_id>/",
        views.CreateFeature.as_view(),
        name="feature-create",
    ),
    path(
        "feature-delete/<int:feature_id>/", views.delete_feature, name="delete-feature"
    ),
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "projetapi-schema"},
        ),
        name="swagger-ui",
    ),
    path("history/<int:project_id>/", views.history),
    path(
        "personal-expenses/<int:expense_id>/delete-update/",
        views.get_delete_update_expenses,
    ),
    path("all-expenses/me/", views.get_all_personal_expenses, name="my-expenses"),
    path(
        "budget-expenses/<int:budget_id>/",
        views.list_expenses_by_budget,
        name="personal-budget-expenses",
    ),
]