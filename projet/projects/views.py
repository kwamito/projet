from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User
from .models import Project
from users.permissions import IsOwnerOrReadOnly
from .serializers import ProjectSerializer
from rest_framework import status

"""
What needs to be done
Create a UserProjectsListView
Create an Update Delete and Detail view
"""

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