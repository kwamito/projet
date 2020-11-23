from django.db import models
from users.models import User, Contributor
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone, timesince
from djmoney.models.fields import MoneyField
from decimal import ROUND_UP

# Create your models here.
class Project(models.Model):
    PRIORITY_CHOICES = [("H", "High"), ("M", "Medium"), ("L", "Low")]
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


class Feature(models.Model):
    PRIORITY_CHOICES = [("H", "High"), ("M", "Medium"), ("L", "Low")]
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
            if self.due_date < timezone.now().date():
                raise ValueError("Due date cannot be in the past.")

        super().save(*args, **kwargs)


class Budget(models.Model):
    FLEXIBILITY_CHOICES = [("F", "Flexible"), ("T", "Tight")]
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=False, blank=False
    )
    project = models.ForeignKey(
        Project,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="budget",
    )
    date_created = models.DateTimeField(auto_now_add=True)
    budget_type = models.CharField(
        choices=FLEXIBILITY_CHOICES, max_length=10, default="F"
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


class Expense(models.Model):
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
    description = models.CharField(max_length=300, null=True, blank=True)
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    date_expended = models.DateTimeField(default=timezone.now())


class PersonalBudget(models.Model):
    name = models.CharField(max_length=210, blank=False, null=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="personal_budgets"
    )
    description = models.TextField(blank=True, null=True)
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True)


class PersonalExpense(models.Model):
    budget = models.ForeignKey(
        PersonalBudget, on_delete=models.CASCADE, related_name="expenses"
    )
    name = models.CharField(max_length=210, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
