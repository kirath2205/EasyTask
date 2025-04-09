import datetime
from django.utils import timezone

from django.db import transaction
from rest_framework import serializers
from .models import *
from EasyTask.settings import redis_client


class PrivateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def validate(self, attrs):
        required_fields = ['title', 'description', 'frequency', 'starts_on', 'ends_on']
        for required_field in required_fields:
            if required_field not in self.initial_data:
                raise serializers.ValidationError({required_field: "This field is required."})
        return attrs

    def validate_ends_on(self, ends_on):
        if ends_on < timezone.now():
            raise serializers.ValidationError("End date cannot be in the past.")
        return ends_on

    def validate_title(self, title):
        if len(title) == 0:
            raise serializers.ValidationError('Empty title ')

        return title

    def validate_description(self, description):
        if len(description) == 0:
            raise serializers.ValidationError('Empty task description')

        return description

    def validate_starts_on(self, starts_on):
        if starts_on < timezone.now():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return starts_on

    def validate_frequency(self, frequency):
        # TODO: validate frequency
        return frequency

    @transaction.atomic
    def create(self, validated_data):
        with transaction.atomic():
            validated_data['created_at'] = timezone.now()
            task = Task.objects.create(**validated_data)
            frequency = validated_data['frequency']
            time_delta = FREQUENCY_TO_DELTA[frequency]
            due_date = validated_data['starts_on'] + time_delta
            subscription = Subscription.objects.create(task=task,
                                                       user=self.context['request'].user,
                                                       starts_on=validated_data.get('starts_on'),
                                                       due_date=due_date,
                                                       ends_on=validated_data.get('ends_on'),
                                                       frequency=validated_data.get('frequency'))
            due_date_epoch_time = int(due_date.timestamp())
            redis_client.set(str(subscription.subscription_id), '', exat=due_date_epoch_time)

            return subscription
