from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.conf import settings
from .models import User, Profile
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects._create_user(
            validated_data["email"], validated_data["password"], False, False
        )
        return user

    class Meta:
        model = User
        fields = ("id", "email", "password")


class UserValidateSerializer(serializers.ModelSerializer):
    def validate(self, validated_data):
        print("Validated data is {}".format(validated_data))
        user = User.objects.get(email=validated_data["email"])
        token = Token.objects.get(user=user)
        return token

    class Meta:
        model = User
        fields = ("id", "email", "password")
