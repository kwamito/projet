from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.ProjectCreateAPI.as_view(), name="project-create"),
    path("my-projects/", views.UsersProjectsList.as_view(), name="users-projects"),
    path(
        "my-project/<int:pk>/",
        views.ProjectDetailUpdateDelete.as_view(),
        name="update-delete",
    ),
]