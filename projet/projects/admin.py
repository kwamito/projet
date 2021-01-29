from django.contrib import admin
from .models import (
    Project,
    Feature,
    Budget,
    BudgetHistory,
    Expense,
    PersonalBudget,
    PersonalExpense,
    Task,
    Team,
)

# Register your models here.
admin.site.register(Project)
admin.site.register(Feature)
admin.site.register(Budget)
admin.site.register(BudgetHistory)
admin.site.register(Expense)
admin.site.register(PersonalBudget)
admin.site.register(PersonalExpense)
admin.site.register(Task)
admin.site.register(Team)