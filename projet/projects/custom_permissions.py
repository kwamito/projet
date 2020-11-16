from users.models import Contributor, User
from projects.models import Project, Expense, Budget, Feature


class TestIfContributor:
    def __init__(self, user, project):
        self.user = user
        self.project = project

    def test_is_contributor_or_manager(self):
        if (
            Contributor.objects.filter(
                user=self.user, project=self.project, accepted=True
            ).exists()
            is not True
            and self.project.user != self.user
        ):
            return False
        else:
            return True
