from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

        def validate_name(self, name):
            if len(name) == 0:
                raise serializers.ValidationError('Empty task name')

        def validate_description(self, description):
            if len(description) == 0:
                raise serializers.ValidationError('Empty task description')

        def create(self, validated_data):
            task = Task(**validated_data)
            task.save()
            return task
