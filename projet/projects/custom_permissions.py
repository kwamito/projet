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

    def test_is_owner_of_feature_and_manager(self, feature):
        if self.user == feature.contributor or self.user == self.project.user:
            return True
        return False


class IsContributorOrDeny:
    def __init__(self, user, project_id):
        self.user = user
        self.project = project_id

    def check_is_contributor(self):
        project = Project.objects.get(id=int(self.project))
        if project.user == self.user:
            return True
        try:
            user_cont = self.user.contributions.get(project=project)
            if user_cont.accepted == False:
                return False
            return True
        except Contributor.DoesNotExist:
            return False