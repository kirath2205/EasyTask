from EasyTask.settings import redis_client
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

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
    def update(self, subscription, validated_data, proof=None):
        with transaction.atomic():
            redis_client.delete(str(f"{subscription.subscription_id}::{Status_enum.IN_PROGRESS.value}"))
            starts_on = subscription.starts_on
            ends_on = subscription.ends_on
            frequency_delta = FREQUENCY_TO_DELTA[subscription.frequency]
            new_starts_on = starts_on + frequency_delta
            new_due_date = new_starts_on + frequency_delta
            subscription_status = validated_data.get('status')

            if subscription_status != Status_enum.COMPLETED:
                snapshot_status = Snapshot_status_enum.FAILED.value
                validated_data['streak'] = 0
            else:
                snapshot_status = Snapshot_status_enum.COMPLETED.value
                validated_data['streak'] = subscription.streak + 1
                validated_data['max_streak'] = max(subscription.max_streak, validated_data['streak'])
            print(snapshot_status)
            snapshot = Snapshot.objects.create(subscription=subscription, proof=proof, started_on=starts_on,
                                               completed_on=new_starts_on, snapshot_status=snapshot_status)
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

    @staticmethod
    def filter_subscriptions(user, request, status=None, page=1, page_size=10):
        subscriptions = Subscription.objects.filter(user=user)

        if status:
            subscriptions = subscriptions.filter(status=status)

        subscriptions = subscriptions.order_by('starts_on')

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginator.page = page
        result_page = paginator.paginate_queryset(subscriptions, request)
        return paginator.get_paginated_response(SubscriptionSerializer(result_page, many=True).data)


class ProofSerializer(serializers.ModelSerializer):
    image_uri = serializers.CharField(write_only=True)
    subscription_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = Proof
        fields = '__all__'

    def validate(self, attrs):
        required_fields = ['subscription_id', 'image_uri']
        for required_field in required_fields:
            if required_field not in self.initial_data:
                raise serializers.ValidationError({required_field: "This field is required."})
        return attrs

    def validate_subscription_id(self, subscription_id):
        if not Subscription.objects.filter(subscription_id=subscription_id).exists():
            raise serializers.NotFound('Subscription not found')

        return subscription_id

    def validate_image_uri(self, image_uri):
        '''
        validate image resource exists in s3
        '''
        print(f"image uri is {image_uri}")
        return image_uri

    @transaction.atomic
    def create(self, validated_data):
        with transaction.atomic():
            self._validated_subscription_id = validated_data.pop("subscription_id", None)
            proof = Proof.objects.create(image_uri=validated_data.get("image_uri"))

            return proof

    def get_subscription_id(self):
        return getattr(self, "_validated_subscription_id", None)



