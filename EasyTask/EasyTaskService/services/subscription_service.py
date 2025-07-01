from typing import Optional, List, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

from ..models import Subscription, Task, Snapshot, Proof, FREQUENCY_TO_DELTA
from ..enums import Status_enum, Snapshot_status_enum, Subscription_enum
from .redis_service import RedisService

User = get_user_model()


class SubscriptionService:
    def __init__(self):
        self.redis_service = RedisService()

    def create_subscription(self, task: Task, user: User, starts_on, ends_on, frequency: str) -> Subscription:
        """Create a new subscription"""
        time_delta = FREQUENCY_TO_DELTA[frequency]
        due_date = starts_on + time_delta

        subscription = Subscription.objects.create(
            task=task,
            user=user,
            starts_on=starts_on,
            due_date=due_date,
            ends_on=ends_on,
            frequency=frequency
        )

        # Set Redis expiry
        self.redis_service.set_subscription_expiry(subscription.subscription_id, due_date)

        return subscription

    def get_subscriptions_paginated(self, user: User, status: Optional[str] = None,
                                    page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated subscriptions for a user"""
        subscriptions = Subscription.objects.filter(user=user)

        if status:
            subscriptions = subscriptions.filter(status=status)

        subscriptions = subscriptions.order_by('starts_on')

        # Calculate pagination
        total_count = subscriptions.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        subscription_page = subscriptions[start_index:end_index]

        has_next = end_index < total_count
        has_previous = page > 1

        return {
            'results': list(subscription_page),
            'count': total_count,
            'next': page + 1 if has_next else None,
            'previous': page - 1 if has_previous else None,
            'page': page,
            'page_size': page_size
        }

    @transaction.atomic
    def update_subscription_status(self, subscription: Subscription,
                                   new_status: str, proof: Optional[Proof] = None) -> Subscription:
        """Update subscription status and create snapshot"""
        with transaction.atomic():
            # Remove existing Redis key
            self.redis_service.delete_subscription_expiry(subscription.subscription_id)

            starts_on = subscription.starts_on
            ends_on = subscription.ends_on
            frequency_delta = FREQUENCY_TO_DELTA[subscription.frequency]
            new_starts_on = starts_on + frequency_delta
            new_due_date = new_starts_on + frequency_delta

            # Determine snapshot status and update streak
            if new_status != Status_enum.COMPLETED.value:
                snapshot_status = Snapshot_status_enum.FAILED.value
                new_streak = 0
            else:
                snapshot_status = Snapshot_status_enum.COMPLETED.value
                new_streak = subscription.streak + 1

            # Create snapshot
            Snapshot.objects.create(
                subscription=subscription,
                proof=proof,
                started_on=starts_on,
                completed_on=new_starts_on,
                snapshot_status=snapshot_status
            )

            # Update subscription
            subscription.streak = new_streak
            subscription.max_streak = max(subscription.max_streak, new_streak)

            if new_starts_on >= ends_on:
                subscription.status = Subscription_enum.COMPLETED.value
            else:
                subscription.status = Subscription_enum.IN_PROGRESS.value
                subscription.starts_on = new_starts_on
                subscription.due_date = new_due_date
                # Set new Redis expiry
                self.redis_service.set_subscription_expiry(subscription.subscription_id, new_due_date)

            subscription.save()
            return subscription

    def get_subscription_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        try:
            return Subscription.objects.get(subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            return None