from rest_framework import serializers
from django.utils import timezone
from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def validate_due_date(self, due_date):
        if due_date < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return due_date

    def validate_name(self, name):
        if len(name) == 0:
            raise serializers.ValidationError('Empty task name')

        return name

    def validate_description(self, description):
        if len(description) == 0:
            raise serializers.ValidationError('Empty task description')

        return description

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        task = Task(**validated_data)
        task.save()
        return task
