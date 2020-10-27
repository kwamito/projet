from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from users.models import User, Profile
from rest_framework import status
from rest_framework.authtoken.models import Token

# Create your tests here.


class TestUserModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="killmonger",
        )

    def test_profile(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)

    def test_token(self):
        token = Token.objects.get(user=self.user)
        self.assertTrue(token)
