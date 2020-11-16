from django.contrib import admin
from django.urls import path
from . import views


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
        "create-feature/<int:project_id>/",
        views.CreateFeature.as_view(),
        name="feature-create",
    ),
    path(
        "feature-delete/<int:feature_id>/", views.delete_feature, name="delete-feature"
    ),
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
    path("feature/<int:pk>/", views.FeatureDetail.as_view(), name="feature-detail"),
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
]