from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import User, Contributor
from .models import Project, Feature
from users.permissions import IsOwnerOrReadOnly
from .serializers import ProjectSerializer, FeatureSerializer
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
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOfProject, IsOwnerOrReadOnly]
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


class CreateFeature(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)

        if (
            Contributor.objects.filter(
                user=request.user, project=project, accepted=True
            ).exists()
            is not True
            and project.user != request.user
        ):
            error = "You have to be an accepted contributor or the project manager before you can make contributions."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        # _mutable = data._mutable

        # # set to mutable
        # data._mutable = True

        # # сhange the values you want

        # # set mutable flag back

        data["project"] = str(project.id)
        data["contributor"] = str(request.user.id)
        # data._mutable = _mutable
        serializer = FeatureSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error = "Could not save feature"
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        error = "Method not allowed"
        return Response(error, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FeatureDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeatureSerializer

    def get_queryset(self):
        return Feature.objects.filter(contributor=self.request.user)


@api_view(["DELETE"])
def delete_feature(request, feature_id=None):
    if request.method == "DELETE":
        try:

            feature = Feature.objects.get(id=feature_id)

            project = feature.project
            if request.user == feature.contributor or request.user == project.user:
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