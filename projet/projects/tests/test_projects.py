from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from users.models import User
from django.urls import reverse
from projects.models import Project


class TestProjectsAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("test@email.com", "killmonger")
        first_project = Project.objects.create(user=self.user, title="Vertigo")
        self.create = reverse("project-create")
        self.users_projects = reverse("users-projects")
        self.detail = reverse("update-delete", args=[first_project.id])
        self.new_user = User.objects.create_user("tes@email.com", "killmonger")
        self.new_project = Project.objects.create(
            user=self.new_user, title="Something testy"
        )

    def test_logged_in_user_can_create(self):
        self.client.force_login(user=self.user)
        data = {"title": "Migron"}
        response = self.client.post(self.create, data=data)
        self.assertEqual(response.status_code, 201)

    def test_logged_out_user_can_create(self):
        data = {"title": "Avion"}
        response = self.client.post(self.create, data=data)
        self.assertEqual(response.status_code, 401)

    def test_user_can_update_project(self):
        self.client.force_login(user=self.user)
        response = self.client.patch(self.detail, data={"title": "Migrain"})
        project = Project.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(project.title, "Migrain")

    def test_user_can_update_others_project(self):
        self.client.force_login(user=self.user)
        update_url = reverse("update-delete", args=[self.new_project.id])
        response = self.client.patch(update_url, data={"title": "Changed"})
        self.assertEqual(response.status_code, 404)
