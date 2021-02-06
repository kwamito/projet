from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from users.models import User, Contributor
from projects.models import Project, Task
from django.urls import reverse


class TestTasks(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@email.com", "testingphase")
        self.project = Project.objects.create(user=self.user, title="New Project")
        self.second_user = User.objects.create_user("tess@email.com", "somethingfiesty")
        self.contributor = Contributor.objects.create(
            user=self.second_user, project=self.project, accepted=True
        )
        self.client = APIClient()

    def test_contributor_can_create_tasks(self):
        self.client.force_login(user=self.user)
        data = {
            "name": "Provide feedback for clients",
            "description": "It is important",
        }
        url = reverse("create-tasks-list", args=[self.project.id])
        response = self.client.post(url, data=data, format="json")
        print(response)
