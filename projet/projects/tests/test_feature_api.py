from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from users.models import User, Contributor
from projects.models import Project, Feature
import json


class TestFeaturesAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("test@email.com", "testingphase")
        self.contributing_user = User.objects.create_user(
            "contri@email.com", "contributions"
        )
        self.unaccepted_contributor = User.objects.create_user(
            "unaccepted@email.com", "unaccepteduser"
        )
        self.project = Project.objects.create(user=self.user, title="A new project")
        self.create_features = reverse("feature-create", args=[self.project.id])
        self.second_user = User.objects.create_user("bean@email.com", "testingphase")
        self.contribution = Contributor.objects.create(
            user=self.contributing_user, project=self.project, accepted=True
        )
        self.unaccepted_contribution = Contributor.objects.create(
            user=self.unaccepted_contributor, project=self.project
        )
        self.feature_creator = User.objects.create_user("me@email.com", "teststinjd")
        Contributor.objects.create(
            user=self.feature_creator, project=self.project, accepted=True
        )
        self.first_feature = Feature.objects.create(
            description="something",
            contributor=self.feature_creator,
            name="A newly created feature",
            project=self.project,
        )
        self.second_feature = Feature.objects.create(
            description="something again",
            contributor=self.feature_creator,
            name="Another created feature",
            project=self.project,
            reviewed=True,
        )

    def test_manager_can_create_features(self):
        self.client.force_login(user=self.user)
        data = {"name": "Users Profile"}
        response = self.client.post(self.create_features, data=data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_non_manager_can_create_features(self):
        self.client.force_login(user=self.contributing_user)
        response = self.client.post(
            self.create_features, data={"name": "New one"}, format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_non_contributor_can_create_features(self):
        self.client.force_login(user=self.second_user)
        response = self.client.post(
            self.create_features, data={"name": "A new pro pro"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_unaccepted_contributor_can_create_features(self):
        self.client.force_login(user=self.unaccepted_contributor)
        response = self.client.post(
            self.create_features, data={"name": "A new pro pro"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_non_owner_can_delete_feature(self):
        feature_delete_url = reverse("delete-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.second_user)
        response = self.client.delete(feature_delete_url, format="json")
        self.assertEqual(response.status_code, 401)

    def test_owner_can_delete_feature(self):
        feature_delete_url = reverse("delete-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.feature_creator)
        response = self.client.delete(feature_delete_url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_manager_can_delete_feature(self):
        feature_delete_url = reverse("delete-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.user)
        response = self.client.delete(feature_delete_url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_contributor_can_review_own_feature(self):
        feature_review_url = reverse("review-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.feature_creator)
        response = self.client.patch(feature_review_url, format="json")
        self.assertEqual(response.status_code, 401)

    def test_manager_can_review_feature(self):
        feature_review_url = reverse("review-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.user)
        response = self.client.patch(feature_review_url, format="json")
        self.assertEqual(response.status_code, 202)

    def test_contributor_can_approve_own_feature(self):
        approve_url = reverse("approve-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.feature_creator)
        response = self.client.patch(approve_url, format="json")
        self.assertEqual(response.status_code, 401)

    def test_unreviewed_feature_can_be_approved(self):
        approve_url = reverse("approve-feature", args=[self.first_feature.id])
        self.client.force_login(user=self.user)
        response = self.client.patch(approve_url, format="json")
        self.assertEqual(response.status_code, 406)

    def test_manager_can_approve_feature(self):
        approve_url = reverse("approve-feature", args=[self.second_feature.id])
        self.client.force_login(user=self.user)
        response = self.client.patch(approve_url, format="json")
        self.assertEqual(response.status_code, 202)
