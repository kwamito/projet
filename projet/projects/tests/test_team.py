from rest_framework.test import APIClient, APITestCase
from users.models import User, Contributor
from projects.models import Project, Task, Team
from django.urls import reverse


class TestTeam(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@email.com", "testbestatit")
        self.project = Project.objects.create(user=self.user, title="A new one")
        self.second_user = User.objects.create_user("rest@email.com", "testatthebest")
        self.contributor = Contributor.objects.create(
            user=self.user, project=self.project, accepted=True
        )
        self.client = APIClient()

    def test_contributor_can_create_team(self):
        self.client.force_login(user=self.second_user)
        url = reverse("team-create", args=[self.project.id])
        data = {"name": "The ux/ui team"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_manager_can_create_team(self):
        self.client.force_login(user=self.user)
        url = reverse("team-create", args=[self.project.id])
        data = {"name": "Another team"}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
