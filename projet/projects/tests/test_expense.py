from rest_framework.test import APIClient, APITestCase
from users.models import User, Contributor
from projects.models import Project, Feature, Expense, Budget
from django.urls import reverse


class TestExpenseAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@email.com", "testingagain")
        self.project = Project.objects.create(user=self.user, title="A new one again")
        self.second_user = User.objects.create_user("tests@email.com", "teststests")
        self.third_user = User.objects.create_user("some@email.com", "sometesting")
        self.unaccepted_contributor = Contributor.objects.create(
            user=self.second_user, project=self.project
        )
        self.accepted_user = Contributor.objects.create(
            user=self.third_user, project=self.project, accepted=True
        )
        self.client = APIClient()

    def test_manager_can_create_expense(self):
        create_expense_url = reverse("expense-create", args=[self.project.id])
        self.client.force_login(user=self.user)
        data = {"amount": 34, "description": "A new expense"}
        response = self.client.post(create_expense_url, data=data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_non_contributor_can_create_expense(self):
        create_expense_url = reverse("expense-create", args=[self.project.id])
        self.client.force_login(user=self.second_user)
        data = {"amount": 34, "description": "A new expense"}
        response = self.client.post(create_expense_url, data=data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_contributor_can_create_expense(self):
        create_expense_url = reverse("expense-create", args=[self.project.id])
        self.client.force_login(user=self.third_user)
        data = {"amount": 34, "description": "A new expense"}
        response = self.client.post(create_expense_url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
