from django.utils import timezone
from rest_framework import serializers

from .models import Task, Subscription, Proof
from .services import ValidationService


class PrivateTaskSerializer(serializers.ModelSerializer):
    """
    Simplified serializer focused only on data validation and serialization
    Business logic moved to services
    """

    class Meta:
        model = Task
        fields = ['title', 'description', 'frequency', 'starts_on', 'ends_on']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_service = ValidationService()

    def validate(self, attrs):
        # Use validation service for business rules
        return attrs

    def validate_ends_on(self, ends_on):
        if ends_on < timezone.now():
            raise serializers.ValidationError("End date cannot be in the past.")
        return ends_on

    def validate_starts_on(self, starts_on):
        if starts_on < timezone.now():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return starts_on


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Simple serializer for subscription data
    """
    task = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['subscription_id', 'task', 'starts_on', 'due_date', 'ends_on',
                  'frequency', 'streak', 'max_streak', 'status']

    def get_task(self, obj):
        return {
            'task_id': str(obj.task.task_id),
            'title': obj.task.title,
            'description': obj.task.description
        }


class ProofSerializer(serializers.ModelSerializer):
    """
    Simple serializer for proof submission
    """
    subscription_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Proof
        fields = ['image_uri', 'subscription_id']

    def validate_image_uri(self, image_uri):
        # Basic validation - detailed validation happens in service layer
        if not image_uri.strip():
            raise serializers.ValidationError("Image URI cannot be empty")
        return image_uri