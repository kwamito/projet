from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import User, Contributor
from .models import Project
from users.permissions import IsOwnerOrReadOnly
from .serializers import ProjectSerializer
from rest_framework import status
from users.serializers import ContributorSerializer
from users.permissions import IsOwnerOrAdminOfProject, IsContributor
import json
from django.utils import timezone
from django.core.exceptions import ValidationError, SuspiciousOperation


# Create your views here.
class ProjectCreateAPI(generics.ListCreateAPIView):
    queryset = Project.objects.filter(is_public=True)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class UsersProjectsList(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class AcceptContributor(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOfProject]
    queryset = Contributor.objects.all()

    def perform_update(self, serializer):
        serializer.save(accepted_by=self.request.user, date_accepted=timezone.now())

    def patch(self, request, project_id=None, contributor_id=None):
        contributor = Contributor.objects.get(id=contributor_id, project__id=project_id)
        if request.user == contributor.user:
            error = "You cannot accept yourself"
            return Response(error, status=status.HTTP_403_FORBIDDEN)

        contributor.accepted = True
        contributor.save()
        return Response(
            f"You have accepted {contributor.user} to contribute to {contributor.project.title}.",
            status=status.HTTP_202_ACCEPTED,
        )


@api_view(["POST"])
def contribute(request, project_id):
    if request.method == "POST":
        project = Project.objects.get(id=project_id)
        if request.user == project.user:
            error = "You are the owner of the project, you cannot become a contributor."
            return Response(error, status=status.HTTP_403_FORBIDDEN)
        try:
            contributor = Contributor.objects.get(user=request.user, project=project)
            error = f"You have already requested to contribute to {project.title}. If you have not been accepted yet wait."
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        except Contributor.DoesNotExist:
            contributor = Contributor.objects.create(user=request.user, project=project)
        jsons = f"You have sent a request to contribute to {project.title}. You'll have to wait to be accepted to start contribution."
        return Response(jsons, status=status.HTTP_400_BAD_REQUEST)


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
