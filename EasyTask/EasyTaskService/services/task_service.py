# EasyTaskService/services/task_service.py
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import Task, Subscription, FREQUENCY_TO_DELTA
from ..enums import Status_enum, Task_type_enum
from .subscription_service import SubscriptionService

User = get_user_model()


class TaskService:
    def __init__(self):
        self.subscription_service = SubscriptionService()

    @transaction.atomic
    def create_private_task(self, user: User, task_data: Dict[str, Any]) -> Subscription:
        """
        Creates a private task and its associated subscription
        """
        with transaction.atomic():
            task = self.__create_task(Task_type_enum.PRIVATE.value, task_data)
            subscription = self.create_subscription(user, task)

            return subscription

    @transaction.atomic
    def create_public_task(self, user: User, task_data: Dict[str, Any]) -> Subscription:
        """
        Creates a brand task
        """
        with transaction.atomic():
            task = self.__create_task(Task_type_enum.PUBLIC.value, task_data)

            return task

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        try:
            return Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return None

    @staticmethod
    def __create_task(task_type: str, task_data):
        task = Task.objects.create(
            title=task_data['title'],
            description=task_data['description'],
            frequency=task_data['frequency'],
            starts_on=task_data['starts_on'],
            ends_on=task_data['ends_on'],
            created_at=timezone.now(),
            task_type=task_type
        )

        return task

    def create_subscription(self, user, task) -> Subscription:
        subscription = self.subscription_service.create_subscription(
            task=task,
            user=user,
            starts_on=task.starts_on,
            ends_on=task.ends_on,
            frequency=task.frequency
        )

        return subscription

    def get_tasks_paginated(self, user, page, page_size, task_type):
        """Return paginated public tasks."""
        tasks = Task.objects.filter(task_type=Task_type_enum.PUBLIC.value).order_by("created_at")

        total_count = tasks.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        tasks_page = tasks[start_index:end_index]

        has_next = end_index < total_count
        has_previous = page > 1

        return {
            "results": list(tasks_page),
            "count": total_count,
            "next": page + 1 if has_next else None,
            "previous": page - 1 if has_previous else None,
            "page": page,
            "page_size": page_size,
        }