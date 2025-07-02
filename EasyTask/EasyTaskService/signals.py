from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Subscription
from .services.milestone_service import MilestoneService


@receiver(post_save, sender=Subscription)
def create_milestones_on_subscription_create(sender, instance, created, **kwargs):
    """Create milestones automatically when a subscription is created."""
    if created:
        service = MilestoneService()
        service.create_milestones(instance)