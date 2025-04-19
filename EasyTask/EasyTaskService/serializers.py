from EasyTask.settings import redis_client
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .enums import Snapshot_status_enum, Status_enum, Subscription_enum
from .models import *


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
            redis_client.set(str(f"{subscription.subscription_id}::{Status_enum.IN_PROGRESS.value}"), '',
                             exat=due_date_epoch_time)

            return subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

    @transaction.atomic
    def update(self, subscription, validated_data):
        with transaction.atomic():
            starts_on = subscription.starts_on
            ends_on = subscription.ends_on
            frequency_delta = FREQUENCY_TO_DELTA[subscription.frequency]
            new_starts_on = starts_on + frequency_delta
            new_due_date = subscription.due_date + frequency_delta
            subscription_status = validated_data.get('status')

            if subscription_status != 'COMPLETED':
                snapshot_status = Snapshot_status_enum.FAILED.value
                validated_data['streak'] = 0
            else:
                snapshot_status = Snapshot_status_enum.COMPLETED.value
                validated_data['streak'] = subscription.streak + 1
                validated_data['max_streak'] = max(subscription.max_streak, validated_data['streak'])
            print(snapshot_status)
            snapshot = Snapshot.objects.create(subscription=subscription, proof=None, started_on=starts_on,
                                               completed_on=ends_on, snapshot_status=snapshot_status)
            if new_starts_on >= ends_on:
                validated_data['status'] = Subscription_enum.COMPLETED
            else:
                validated_data['status'] = Subscription_enum.IN_PROGRESS
                validated_data['starts_on'] = new_starts_on
                validated_data['due_date'] = new_due_date
                redis_client.set(str(f"{subscription.subscription_id}::{Status_enum.IN_PROGRESS.value}"), '',
                                 exat=new_due_date)

            for attr, value in validated_data.items():
                setattr(subscription, attr, value)
            subscription.save()

            return subscription


