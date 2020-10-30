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
from .models import User, Profile
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .serializers import UserSerializer, UserValidateSerializer, ProfileSerializer
from .permissions import IsOwnerOrReadOnly


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
            if len(serializer.data["password"]) < 8:
                json = serializer.data
                json["error"] = "Password should be more than 8 characters long"
                return Response(json, status=status.HTTP_400_BAD_REQUEST)

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
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileList(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer