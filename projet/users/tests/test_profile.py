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
        self.second_user = User.objects.create_user("tests@email.com", "killmonger")
        self.create_user_url = reverse("create")
        self.login_url = reverse("login")
        self.client = APIClient()
        self.profile_url = reverse("profile", args=[self.user.id])

    def test_profile_without_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 401)

    def test_profile_with_login(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

    def test_user_update_others_profile(self):
        profile_detail_url = reverse("profile", args=[self.second_user.id])
        self.client.force_login(user=self.user)
        data = {"bio": "Just living"}
        response = self.client.patch(profile_detail_url, data=data)
        self.assertEqual(response.status_code, 403)

    def test_user_update_own_profile(self):
        profile_detail_url = reverse("profile", args=[self.user.id])
        self.client.force_login(user=self.user)
        data = {"bio": "Just living"}
        response = self.client.patch(profile_detail_url, data=data)
        self.assertEqual(response.status_code, 200)
