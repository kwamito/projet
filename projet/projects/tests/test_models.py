from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from users.models import User
from projects.models import Project
from datetime import datetime


# Create your tests here.


class TestProjectModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@email.com", "killmonger")

    def test_project_due_date(self):
        due_date = "2023-12-21"
        date = datetime.strptime(due_date, "%Y-%m-%d").date()
        project = Project.objects.create(user=self.user, due_date=date)

    def test_project(self):
        pro = Project.objects.create(user=self.user, is_public=False, priority="H")
