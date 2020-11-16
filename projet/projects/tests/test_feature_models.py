from django.test import TestCase
from projects.models import Feature, Project
from users.models import User, Contributor


class TestFeatures(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@email.com", "testeduser")
        self.second_user = User.objects.create_user("sec@email.com", "seconduser")
        self.project = Project.objects.create(user=self.user, title="First Project")
        self.contributor = Contributor.objects.create(
            user=self.user, project=self.project, accepted=True
        )

    def test_unapproved_contributor_can_create_feature(self):
        feature = Feature.objects.create(
            contributor=self.user,
            project=self.project,
            description="First feature",
            name="A new name",
        )
