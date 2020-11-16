from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from users.models import Contributor, User
from projects.models import Project
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied


class TestProjectContributionAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("test@email.com", "killmonger")
        self.second_user = User.objects.create_user("second@email.com", "killmonger")
        self.third_user = User.objects.create_user(
            "contributor@email.com", "contributings"
        )
        self.project = Project.objects.create(user=self.user, title="A new one")
        self.second_project = Project.objects.create(
            user=self.second_user, title="Second one"
        )
        self.contribution = Contributor.objects.create(
            user=self.third_user, project=self.project
        )
        self.project_list_create = reverse("project-create")
        self.users_projects = reverse("users-projects")
        self.project_detail = reverse("update-delete", args=[self.project.id])
        self.accept_contributor = reverse(
            "accept-contribution", args=[self.project.id, self.contribution.id]
        )
        self.project_contributions = reverse("contributors", args=[self.project.id])
        self.project_contributions_status = reverse(
            "pending-accepted-contributors", args=[self.project.id, "accepted"]
        )

    def test_owner_can_be_contributor(self):
        self.client.force_login(user=self.second_user)
        contribute_url = reverse("contribute", args=[self.second_project.id])
        response = self.client.post(contribute_url, format="json")

        self.assertEqual(response.status_code, 403)

    def test_contributor_can_offer_twice(self):
        self.client.force_login(user=self.third_user)
        contribute_url = reverse("contribute", args=[self.project.id])
        response = self.client.post(contribute_url, format="json")
        self.assertEqual(response.status_code, 400)

    def test_manager_can_accept_contribution(self):
        self.client.force_login(user=self.user)
        accept_url = reverse(
            "accept-contribution", args=[self.project.id, self.contribution.id]
        )

        response = self.client.patch(accept_url, data={"accepted": True}, format="json")
        cont = Contributor.objects.get(project=self.project.id)

        self.assertEqual(response.status_code, 202)

    def test_contributor_can_accept_self(self):
        self.client.force_login(user=self.third_user)
        accept_url = reverse(
            "accept-contribution", args=[self.project.id, self.contribution.id]
        )
        response = self.client.patch(
            accept_url, data={"accepted": "true"}, format="json"
        )
        cont = Contributor.objects.first()
        print(cont.accepted)
        self.assertEqual(response.status_code, 403)