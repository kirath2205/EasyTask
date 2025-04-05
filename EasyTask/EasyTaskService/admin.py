from django.contrib import admin

from .models import *


# Register your models here.
class TaskServiceAdmin(admin.ModelAdmin):
    model = Task


class CompanyServiceAdmin(admin.ModelAdmin):
    model = Company


class TermsAdmin(admin.ModelAdmin):
    model = Terms


class ProofAdmin(admin.ModelAdmin):
    model = Proof


class RequirementAdmin(admin.ModelAdmin):
    model = Requirement


class RewardAdmin(admin.ModelAdmin):
    model = Reward


class TaskAdmin(admin.ModelAdmin):
    model = Task


class SubscriptionAdmin(admin.ModelAdmin):
    model = Subscription


class SnapshotAdmin(admin.ModelAdmin):
    model = Snapshot


admin.site.register(Task, TaskServiceAdmin)
