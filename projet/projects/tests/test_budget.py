from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from users.models import User, Contributor
from projects.models import Project, Budget, Expense, BudgetHistory
from django.urls import reverse


class TestBudgetsAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@email.com", "killmonger")
        self.project = Project.objects.create(user=self.user, title="A new one")
        self.second_user = User.objects.create_user(
            "testing@email.com", "testingwasfun"
        )
        self.create_budget_url = reverse("budget-create", args=[self.project.id])
        self.client = APIClient()
        budget = Budget.objects.create(project=self.project, amount=223)
        self.second_project = Project.objects.create(title="Something", user=self.user)

    def test_noncontributor_can_create_budget(self):
        self.client.force_login(user=self.second_user)
        create_url = reverse("budget-create", args=[self.second_project.id])
        data = {"amount": 3454}
        response = self.client.post(create_url, data=data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_manager_can_update(self):
        self.client.force_login(user=self.second_user)
        data = {"amount": 4000}
        update_url = reverse("budget-create", args=[self.project.id])
        response = self.client.patch(update_url, data=data, format="json")
        self.assertEqual(response.status_code, 401)
