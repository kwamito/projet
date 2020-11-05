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
]