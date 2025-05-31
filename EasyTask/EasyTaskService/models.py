import uuid
import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings

FREQUENCY_CHOICES = [
    ('NONE', datetime.timedelta(minutes=0)),
    ('MINUTE', datetime.timedelta(minutes=1)),
    ('HOURLY', datetime.timedelta(hours=1)),
    ('DAILY', datetime.timedelta(days=1)),
    ('WEEKLY', datetime.timedelta(weeks=1)),
    # ('MONTHLY', relativedelta(months=1)),
]

FREQUENCY_TO_DELTA = {
    'NONE': datetime.timedelta(minutes=0),
    'MINUTE': datetime.timedelta(minutes=1),
    'HOURLY': datetime.timedelta(hours=1),
    'DAILY': datetime.timedelta(days=1),
    'WEEKLY': datetime.timedelta(weeks=1),
    'MONTHLY': relativedelta(months=1),
}
TASK_TYPE = [
    ('PUBLIC', 'PUBLIC'),
    ('PRIVATE', 'PRIVATE'),
]

STATUS = [
    ('UPCOMING', 'UPCOMING'),
    ('IN_PROGRESS', 'IN_PROGRESS'),
    ('COMPLETED', 'COMPLETED'),
    ('OVERDUE', 'OVERDUE')
]

SNAPSHOT_STATUS = [
    ('COMPLETED', 'COMPLETED'),
    ('FAILED', 'FAILED')
]


class Company(models.Model):
    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='')
    logo = models.CharField(max_length=200, default='')
    website = models.CharField(max_length=200, default='')


class Terms(models.Model):
    term_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=200, default='')


class Proof(models.Model):
    proof_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_uri = models.CharField(max_length=200, default='')


class Requirement(models.Model):
    requirement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=200, default='')
    examples = ArrayField(models.CharField(max_length=100), null=True, blank=True)


class Reward(models.Model):
    reward_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, default='')
    code = models.CharField(max_length=300, default='')
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    terms = models.ForeignKey("Terms", on_delete=models.CASCADE)


class Task(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='NONE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reward = models.ForeignKey("Reward", on_delete=models.CASCADE, null=True, blank=True)
    requirement = models.ForeignKey("Requirement", on_delete=models.CASCADE, null=True, blank=True)
    starts_on = models.DateTimeField()
    ends_on = models.DateTimeField()
    task_type = models.CharField(max_length=10, choices=TASK_TYPE, default='PRIVATE')


class Subscription(models.Model):
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    starts_on = models.DateTimeField()
    due_date = models.DateTimeField()
    ends_on = models.DateTimeField()
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='NONE'
    )
    streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default='UPCOMING'
    )

    def get_task(self):
        return self.task


class Snapshot(models.Model):
    snapshot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE)
    proof = models.ForeignKey("Proof", on_delete=models.CASCADE, null=True, blank=True)
    started_on = models.DateTimeField()
    completed_on = models.DateTimeField()
    snapshot_status = models.CharField(max_length=20, default='FAILED')

# class ArchiveSubscription(models.Model):
#     subscription_id = models.IntegerField(primary_key=True, editable=False)
#     task = models.ForeignKey("Task")
#     user = models.ForeignKey(settings.AUTH_USER_MODEL)
#     starts_on = models.DateTimeField()
#     due_date = models.DateTimeField()
#     end_on = models.DateTimeField()
#     frequency = models.CharField(
#         max_length=20,
#         choices=FREQUENCY_CHOICES,
#     )
#     streak = models.IntegerField(default=0)
#     max_streak = models.IntegerField(default=0)
#     status = models.CharField(
#         max_length=30,
#         choices=STATUS,
#     )
#
# class ArchiveSnapshot(models.Model):
#     snapshot_id = models.IntegerField(primary_key=True,editable=False)
#     subscription = models.ForeignKey("Subscription")
#     proof = models.ForeignKey("Proof", on_delete=models.CASCADE)
#     started_on = models.DateTimeField()
#     ended_on = models.DateTimeField()
#     snapshot_status = models.CharField(max_length=20, choices=SNAPSHOT_STATUS, default='FAILED')
