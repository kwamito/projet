from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from users.models import User, Profile, Contributor
from projects.models import Project
from rest_framework import status
from rest_framework.authtoken.models import Token

# Create your tests here.


class TestUserModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="killmonger",
        )
        self.project = Project.objects.create(user=self.user, title="New one")
        self.second_user = User.objects.create_user(
            "testuser@email.com", "contributions"
        )

    def test_user_can_ask_more_than_once(self):
        Contributor.objects.create(user=self.second_user, project=self.project)
        Contributor.objects.create(user=self.second_user, project=self.project)
