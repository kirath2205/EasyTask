from django.db import models
from django.conf import settings
import uuid


class Task(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    FREQUENCY_CHOICES = [
        ('NONE', 'No Repeat'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MED', 'Medium'),
        ('HIGH', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='NONE'
    )
    due_date = models.DateTimeField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default='ongoing')
    failure_reason = models.CharField(max_length=1024, default='')

    def __str__(self):
        return f"{self.name} (User: {self.user.username})"


'''
todo: Add reward model
Enum for public or private tasks
'''
