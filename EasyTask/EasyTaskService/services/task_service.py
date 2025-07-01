# EasyTaskService/services/task_service.py
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import Task, Subscription, FREQUENCY_TO_DELTA
from ..enums import Status_enum
from .subscription_service import SubscriptionService
from .redis_service import RedisService

User = get_user_model()


class TaskService:
    def __init__(self):
        self.subscription_service = SubscriptionService()
        self.redis_service = RedisService()

    @transaction.atomic
    def create_private_task(self, user: User, task_data: Dict[str, Any]) -> Subscription:
        """
        Creates a private task and its associated subscription
        """
        with transaction.atomic():
            # Create task
            task = Task.objects.create(
                title=task_data['title'],
                description=task_data['description'],
                frequency=task_data['frequency'],
                starts_on=task_data['starts_on'],
                ends_on=task_data['ends_on'],
                created_at=timezone.now(),
                task_type='PRIVATE'
            )

            # Create subscription using subscription service
            subscription = self.subscription_service.create_subscription(
                task=task,
                user=user,
                starts_on=task_data['starts_on'],
                ends_on=task_data['ends_on'],
                frequency=task_data['frequency']
            )

            return subscription

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        try:
            return Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return None
