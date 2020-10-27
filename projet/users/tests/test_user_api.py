from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from users.models import User, Profile
from rest_framework import status
from rest_framework.authtoken.models import Token

# Create your tests here.


class TestUserModels(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tes@email.com", "killmonger")
        self.create_user_url = reverse("create")
        self.login_url = reverse("login")
        self.client = APIClient()

    def test_user_create(self):
        data = {"email": "test@email.com", "password": "killmonger"}
        self.client.post(self.create_user_url, data=data, format="json")
        user = User.objects.get(email="test@email.com")
        self.assertEqual(data.get("email"), user.email)

    def test_user_login(self):
        data = {"email": "tes@email.com", "password": "killmonger"}
        response = self.client.post(self.login_url, data=data)
        user = User.objects.get(email="tes@email.com")
        token = Token.objects.get(user=user)
        self.assertEqual(response.data, token.__str__())
