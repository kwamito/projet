from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
import json
from rest_framework.decorators import api_view
from rest_framework import mixins, generics
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .serializers import UserSerializer, UserValidateSerializer


# Create your views here.
class UserCreate(APIView):
    def post(self, request, format="json"):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.get(user=user)

                json = serializer.data
                json["token"] = token.__str__()
                return Response(json, status=status.HTTP_201_CREATED)
        elif serializer.is_valid() != True:
            if len(serializer.data["email"]) < 8:
                json = serializer.data
                json["error"] = "Password should be more than 8 characters long"
                return Response()
            if User.objects.get(email=serializer.data["email"]) == True:
                json = serializer.data
                json[
                    "error"
                ] = "User already exists if you already have an account, login"
                return Response(json, status=status.HTTP_401_UNAUTHORIZED)

        else:
            json = serializer.data
            json["error"] = "Unknown error"
            return Response(json, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
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
