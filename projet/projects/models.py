from django.db import models
from users.models import User, Contributor
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone, timesince
from django.utils.timesince import timesince, timeuntil
from django.contrib.humanize.templatetags import humanize
from djmoney.models.fields import MoneyField
from decimal import ROUND_UP
from datetime import timedelta

PRIORITY_CHOICES = [("H", "High"), ("M", "Medium"), ("L", "Low")]

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255, null=False, blank=False)
    is_public = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now())
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=5, choices=PRIORITY_CHOICES, default="M")
    documentation = models.TextField(null=True, blank=True)
    icon = models.ImageField(upload_to="icons", blank=True, null=True)

    def save(self, *args, **kwargs):

        if self.due_date is not None:
            if self.due_date < timezone.now().date():
                raise ValueError("Due date cannot be in the past.")

        super().save(*args, **kwargs)

    def count_contributors(self):
        return self.contributors.count()

    def total_expenditure(self):
        try:
            expenses = Expense.objects.filter(project__id=self.id)
            total = 0
            for amount in expenses:
                total += amount.amount.amount
            return total
        except Expense.DoesNotExist:
            return ""

    def over_budget_by(self):
        try:
            budget = Budget.objects.get(project__id=self.id)
            expenses = Expense.objects.filter(project__id=self.id)
            budget_amount = budget.amount.amount
            total = 0
            for value in expenses:
                total += value.amount.amount
            if total > budget_amount:
                over = total - budget_amount
                return f"Over budget by {budget.amount_currency}{over}"
            else:
                return f""
        except Budget.DoesNotExist:
            return ""

    def over_budget_by_percentage(self):
        try:
            budget = Budget.objects.get(project__id=self.id)
            expenses = Expense.objects.filter(project__id=self.id)
            budget_amount = budget.amount.amount
            total = 0
            percentage = 0
            for value in expenses:
                total += value.amount.amount
            if total > budget_amount:
                percentage = total - budget_amount
                percentage = percentage / budget_amount
                percentage = percentage * 100
                percentage = round(percentage)
                return f"{percentage}%"
            else:
                return ""
        except Budget.DoesNotExist:
            return ""

    def budget_by_pure_number(self):
        try:
            budget = Budget.objects.get(project__id=self.id)
            expenses = Expense.objects.filter(project__id=self.id)
            budget_amount = budget.amount.amount
            total = 0
            percentage = 0
            for value in expenses:
                total += value.amount.amount
            if total > budget_amount:
                percentage = total - budget_amount
                percentage = percentage / budget_amount
                percentage = percentage * 100
                percentage = round(percentage)
                return f"{percentage}"
            else:
                return self.budget_percent()
        except Budget.DoesNotExist:
            return ""

    def time_since_created(self):
        return humanize.naturaltime(self.created)

    def tasks_completed(self):
        tasks = Task.objects.filter(project__id=self.id)

        if tasks.exists():
            number_of_tasks = tasks.count()
            number_of_completed_tasks = tasks.filter(completed=True).count()
            percetage_of_completed_tasks = (
                number_of_completed_tasks / number_of_tasks * 100
            )
            return percetage_of_completed_tasks
        else:
            return 0

    def tasks_done(self):
        tasks = Task.objects.filter(project__id=self.id)

        if tasks.exists():
            number_of_tasks = tasks.count()
            number_of_completed_tasks = tasks.filter(completed=True).count()
            tasks_completed = f"{number_of_completed_tasks}/{number_of_tasks}"
            return tasks_completed
        else:
            return "0/0"

    def budget_percent(self):
        try:
            budget = Budget.objects.get(project__id=self.id)
            expenses = Expense.objects.filter(project__id=self.id)
            budget_amount = budget.amount.amount
            total = 0
            return budget_amount
            for value in expenses:
                total += value.amount.amount
            if total > budget_amount:
                return self.over_budget_by_percentage()
            else:
                on_budget_by_percentage = total / budget_amount * 100
                return on_budget_by_percentage
        except Budget.DoesNotExist:
            return ""

    def number_of_completed_tasks(self):
        completed_tasks = Task.objects.filter(project__id=self.id, completed=True)
        return completed_tasks.count()

    def all_tasks_count(self):
        all_tasks = Task.objects.filter(project__id=self.id)
        return all_tasks.count()

    def all_uncompleted_tasks(self):
        uncompleted_tasks = Task.objects.filter(project__id=self.id, completed=False)
        return uncompleted_tasks.count()

    def weeks_tasks(self):
        some_day_last_week = timezone.now().date() - timedelta(days=7)
        some_day_last_two_weeks = timezone.now().date() - timedelta(days=14)
        some_day_last_three_weeks = timezone.now().date() - timedelta(days=21)
        some_day_last_four_weeks = timezone.now().date() - timedelta(days=28)
        some_day_last_five_weeks = timezone.now().date() - timedelta(days=35)
        monday_of_last_two_weeks = some_day_last_two_weeks - timedelta(
            days=some_day_last_two_weeks.isocalendar()[2] - 1
        )
        monday_of_last_three_weeks = some_day_last_three_weeks - timedelta(
            days=some_day_last_three_weeks.isocalendar()[2] - 1
        )
        monday_of_last_four_weeks = some_day_last_three_weeks - timedelta(
            days=some_day_last_four_weeks.isocalendar()[2] - 1
        )
        monday_of_last_five_weeks = some_day_last_three_weeks - timedelta(
            days=some_day_last_five_weeks.isocalendar()[2] - 1
        )
        monday_of_last_week = some_day_last_week - timedelta(
            days=(some_day_last_week.isocalendar()[2] - 1)
        )
        print(
            f"last week {monday_of_last_week} two weeks ago {monday_of_last_two_weeks}"
        )
        monday_of_this_week = monday_of_last_week + timedelta(days=7)
        tasks = Task.objects.filter(
            date_created__gte=monday_of_last_week, date_created__lt=monday_of_this_week
        )
        last_two_weeks_tasks = Task.objects.filter(
            date_created__gte=monday_of_last_two_weeks,
            date_created__lt=monday_of_last_week,
        )
        last_three_weeks_tasks = Task.objects.filter(
            date_created__gte=monday_of_last_three_weeks,
            date_created__lt=monday_of_last_two_weeks,
        )
        last_four_weeks_tasks = Task.objects.filter(
            date_created__gte=monday_of_last_four_weeks,
            date_created__lt=monday_of_last_three_weeks,
        )
        last_five_weeks_tasks = Task.objects.filter(
            date_created__gte=monday_of_last_five_weeks,
            date_created__lt=monday_of_last_four_weeks,
        )
        arr = [
            last_five_weeks_tasks.count(),
            last_four_weeks_tasks.count(),
            last_three_weeks_tasks.count(),
            last_two_weeks_tasks.count(),
            tasks.count(),
        ]
        return arr


class Feature(models.Model):

    contributor = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="features",
    )
    project = models.ForeignKey(
        Project,
        related_name="features",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    documentation = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    date_reviewed = models.DateTimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    merged = models.BooleanField(default=False)
    date_merged = models.DateTimeField(blank=True, null=True)
    cost = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=5, default="M")
    votes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):

        if self.due_date is not None:
            if self.due_date.date() < timezone.now().date():
                raise ValueError("Due date cannot be in the past.")

        super().save(*args, **kwargs)

    def time_since_created(self):
        return humanize.naturaltime(self.date_created)
        # return timesince(self.date_created)

    def time_since_reviewed(self):
        return humanize.naturaltime(self.date_reviewed)

    def time_since_merged(self):
        return humanize.naturaltime(self.date_merged)

    def time_to_due_date(self):
        if self.due_date is not None:
            return timeuntil(self.due_date)
        else:
            return None

    def feature_creator_profile_image(self):
        profile_image = self.contributor.profile.image
        return ""


class BaseBudget(models.Model):
    FLEXIBILITY_CHOICES = [("F", "Flexible"), ("T", "Tight")]
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=False, blank=False
    )
    date_created = models.DateTimeField(auto_now_add=True)
    budget_type = models.CharField(
        choices=FLEXIBILITY_CHOICES, max_length=10, default="F"
    )

    class Meta:
        abstract = True


class BaseExpense(models.Model):
    description = models.CharField(max_length=300, null=True, blank=True)
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    date_expended = models.DateTimeField(default=timezone.now())

    class Meta:
        abstract = True


class Budget(BaseBudget):
    project = models.ForeignKey(
        Project,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="budget",
    )

    def get_project(self):
        return Project.objects.get(id=self.project.id)

    def __str__(self):
        return f"{self.amount_currency}{self.amount}"


class BudgetHistory(models.Model):
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="history",
    )
    from_amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    to_amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    date_updated = models.DateTimeField(default=timezone.now())

    def determine(self):
        if self.to_amount < self.from_amount:
            return "Decrease"
        elif self.to_amount > self.from_amount:
            return "Increase"
        else:
            return ""

    def __str__(self):
        return f"From {self.from_amount} to {self.to_amount}"


class Expense(BaseExpense):
    contributor = models.ForeignKey(
        User, on_delete=models.PROTECT, null=False, blank=False, related_name="expenses"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="spendings",
    )

    def contributor_email(self):
        return self.contributor.email

    def total_expenses(self):
        total = 0
        expenses = Expense.objects.filter(project=self.project)
        for expense in expenses:
            total += expense.amount.amount
        return total


class PersonalBudget(BaseBudget):
    name = models.CharField(max_length=210, blank=False, null=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="personal_budgets"
    )
    description = models.TextField(blank=True, null=True)


class PersonalExpense(BaseExpense):
    budget = models.ForeignKey(
        PersonalBudget, on_delete=models.CASCADE, related_name="expenses"
    )
    name = models.CharField(max_length=210, null=False, blank=False)


class Task(models.Model):
    THEMES = [
        ("DP", "#E20142"),
        ("IDR", "#CD5C5C"),
        ("TQ", "#26A69A"),
        ("OR", "#FB8C00"),
        ("DPO", "#FB8C00"),
        ("YLLW", "#FDD835"),
        ("BLUE", "#29B6F6"),
    ]
    STATUS = [
        ("EX", "Expired"),
        ("TMTD", "Terminated"),
        ("CMPTD", "Completed"),
        ("PSD", "Paused"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=5, default="M")
    date_completed = models.DateTimeField(blank=True, null=True)
    assignees = models.ManyToManyField(
        Contributor, related_name="tasks", null=True, blank=True
    )
    theme = models.CharField(choices=THEMES, max_length=15, default="DP")
    completed_by = models.ForeignKey(
        Contributor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="completed_tasks",
    )

    def assignees_names(self):
        assignees = self.assignees.all()
        list_of_names = []
        if assignees is not None:
            for i in assignees:
                list_of_names.append(i.user.email)
                return list_of_names

        else:
            return []

    def total_number_of_assignees(self):
        if self.assignees is not None:
            return self.assignees.count()
        else:
            return 0

    def time_to_start_date(self):
        if self.start_date is not None:
            until = timeuntil(self.start_date)
            print(until)
            if until is None:
                return "Expired"
            return until
        else:
            return "NOT SET"

    def time_to_due_date(self):
        if self.due_date is not None:
            until = timeuntil(self.due_date)
            if until == "0 minutes":
                return "DUE"
            else:
                return until
        else:
            return None


class Team(models.Model):
    name = models.CharField(max_length=200)
    contributors = models.ManyToManyField(Contributor, related_name="teams", blank=True)
    tasks = models.ManyToManyField(Task, related_name="teams", blank=True)
    date_created = models.DateTimeField(default=timezone.now())
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="teams")

    def contributors_names(self):
        names = []
        contributors = self.contributors.all()
        if contributors is not None:
            for user in contributors:
                names.append(user.user.email)
        return names