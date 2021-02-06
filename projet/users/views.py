from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
import json
from rest_framework.decorators import api_view
from rest_framework import mixins, generics
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import User, Profile, Contributor
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .serializers import (
    UserSerializer,
    UserValidateSerializer,
    ProfileSerializer,
    UserBulkSerializer,
)
from .permissions import IsOwnerOrReadOnly
from rest_framework import filters
from django.core.mail import send_mail
from django.conf import settings
from projects.models import Project
from django.shortcuts import get_object_or_404

# Create your views here.
class UserCreate(APIView):
    """
    We allow any since this is a users create/register
    view and no authentication is needed for that
    """

    permission_classes = [AllowAny]

    def post(self, request, format="json"):
        serializer = UserSerializer(data=request.data)
        # If the data passed into the serializer is valid we save it
        if serializer.is_valid():

            user = serializer.save()
            if user:
                token = Token.objects.get(user=user)

                json = serializer.data
                json["token"] = token.__str__()
                return Response(json, status=status.HTTP_201_CREATED)

        elif serializer.is_valid() != True:
            if len(serializer.data["password"]) < 8:
                json = serializer.data
                json["error"] = "Password should be 8 characters or longer"
                return Response(json, status=status.HTTP_400_BAD_REQUEST)
            # Otherwise
            try:
                User.objects.get(email=serializer.data["email"])
                json = serializer.data
                json[
                    "error"
                ] = "User already exists if you already have an account, login"
                return Response(json, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                pass

        else:
            json = serializer.data
            json["error"] = "Unknown error"
            return Response(json, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
    # Also allow any because it's a login view
    permission_classes = [AllowAny]

    def post(self, request, format="json"):
        user_email = request.data["email"]
        user_password = request.data["password"]
        try:
            user = User.objects.get(email=user_email)
            validator = check_password(user_password, user.password)
        except User.DoesNotExist:
            error = "Account does not exist."
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        if validator is not False:
            user = User.objects.get(email=user_email)
            token = Token.objects.get(user=user)
            response = token.__str__()

            return Response(response, status=status.HTTP_200_OK)
        else:
            response = "Wrong password or username"
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class ListUsers(generics.ListAPIView):
    """
    No need for the permissions classes to be defined
    because it's defined in the settings, unless we want
    to add another permissions apart from the IsAuthenticated
    """

    search_fields = ["email", "first_name", "last_name"]
    filter_backends = (filters.SearchFilter,)

    queryset = User.objects.all()
    serializer_class = UserBulkSerializer


def send_invite(project, recipient, sender=None):
    send_mail(
        "Projet",
        f"You have been asked by {sender.email} to contribute to {project.title}. Accept at http://192.168.8.102:3000/accept/6",
        recipient_list=[recipient.email],
        from_email=settings.EMAIL_HOST,
    )

    Contributor.objects.create(user=recipient, project=project)
    return "Email sent"


@api_view(["POST"])
def invite(request):
    if request.method == "POST":

        project_id = request.data["id"]
        project = Project.objects.get(id=int(project_id))
        if project.user != request.user:
            error = "Only project owners/managers can send invites"
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)
        recipient_email = request.data["email"]
        recipient = User.objects.filter(email=recipient_email)
        if request.user == recipient[0]:
            error = "You are trying to invite yourself to this project"
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        if request.user == recipient:
            error = "You are the owner/manager of this project."
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        recipient_contribution = recipient[0].contributions.filter(project=project)

        if recipient_contribution in project.contributors.all():
            error = f"{recipient.email} has already been invited"
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if recipient.exists() is False:
            error = "User needs to have an account."
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        is_contributor = Contributor.objects.filter(user=recipient[0], project=project)
        if is_contributor.exists() == True:
            error = "This user has already been invited"
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        res = send_invite(project=project, recipient=recipient[0], sender=request.user)
        return Response(res, status=status.HTTP_201_CREATED)


class ProfileList(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = ProfileSerializer

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def get_queryset(self):
        return self.get_object()
