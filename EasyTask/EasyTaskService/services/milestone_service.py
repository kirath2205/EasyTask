from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

from ..models import FREQUENCY_TO_DELTA, Milestone


class MilestoneService:
    """Simple service for creating and managing milestones"""

    @transaction.atomic
    def create_milestones(self, subscription):
        """Create milestones for a subscription based on its frequency"""

        # Clear existing milestones
        Milestone.objects.filter(subscription=subscription).delete()

        # Get frequency delta
        frequency_delta = FREQUENCY_TO_DELTA.get(subscription.frequency)

        if not frequency_delta or subscription.frequency == 'NONE':
            # Single milestone for entire period
            self._create_milestone(subscription, subscription.starts_on, subscription.ends_on)
            return 1

        # Create milestones based on frequency
        milestones_created = 0
        current_date = subscription.starts_on

        while current_date <= subscription.ends_on:
            # Calculate end date for this milestone
            if isinstance(frequency_delta, relativedelta):
                next_date = current_date + frequency_delta
            else:
                next_date = current_date + frequency_delta

            milestone_end = min(next_date - timedelta(seconds=1), subscription.ends_on)

            self._create_milestone(subscription, current_date, milestone_end)
            milestones_created += 1
            current_date = next_date

        return milestones_created

    def _create_milestone(self, subscription, start_date, end_date):
        """Create a single milestone"""
        return Milestone.objects.create(
            subscription=subscription,
            user=subscription.user,
            started_on=start_date,
            ends_on=end_date,
            completed_on=None,
            is_completed=False
        )

    def complete_milestone(self, milestone_id):
        """Mark milestone as completed"""
        milestone = Milestone.objects.get(milestone_id=milestone_id)
        milestone.is_completed = True
        milestone.completed_on = timezone.now()
        milestone.save()
        return milestone

    def get_active_milestone(self, subscription):
        """Return the milestone currently active for a subscription."""
        now = timezone.now()
        print("now:", now)
        try:
            return Milestone.objects.get(
                subscription=subscription,
                started_on__lte=now,
                ends_on__gte=now,
            )
        except Milestone.DoesNotExist:
            return None
