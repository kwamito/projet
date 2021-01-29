from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.conf import settings
from .models import User, Profile, Contributor
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)
    image = serializers.ImageField(source="profile.image", required=False)
    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)

    def create(self, validated_data):
        print(validated_data)
        user = User.objects._create_user(
            validated_data["email"],
            validated_data["password"],
            False,
            False,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "image")


class UserBulkSerializer(serializers.Serializer):
    email = serializers.EmailField(read_only=True)
    image = serializers.ImageField(read_only=True, source="profile.image")
    bio = serializers.CharField(read_only=True, source="profile.bio")


class UserValidateSerializer(serializers.ModelSerializer):
    def validate(self, validated_data):
        print("Validated data is {}".format(validated_data))
        user = User.objects.get(email=validated_data["email"])
        token = Token.objects.get(user=user)
        return token

    class Meta:
        model = User
        fields = ("id", "email", "password")


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="user.email")
    date_joined = serializers.ReadOnlyField(source="user.date_joined")

    class Meta:
        model = Profile
        fields = (
            "email",
            "date_joined",
            "first_name",
            "last_name",
            "image",
            "bio",
        )


class ContributorSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(
        source="user.profile.image", read_only=True, required=False
    )
    user_email = serializers.ReadOnlyField(source="user.email")
    accepted_date = serializers.ReadOnlyField(source="date_accepted")
    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = Contributor
        fields = (
            "user",
            "user_email",
            "accepted",
            "accepted_by",
            "id",
            "profile_image",
            "accepted_date",
            "project_id",
            "project_name",
        )
