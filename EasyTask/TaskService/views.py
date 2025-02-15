from django.shortcuts import render
from requests import Response

from rest_framework import status
from rest_framework.decorators import api_view

from .serializers import TaskSerializer


# Create your views here.
@api_view(['POST'])
def create_task(request):
    task_payload = request.data
    serialized_task = TaskSerializer(data=task_payload)
    if serialized_task.is_valid():
        serialized_task.save()
        task_id = serialized_task.validated_data.get('task_id')
        return Response({'message': f'Task {task_id} created successfully'}, status=status.HTTP_201_CREATED)

'''
Create views for google to handle auth via django-rest-auth
create utility singletons for extracting user-id from jwt token in header and return user reference
use user reference to link tasks in task service serializer to users then save task
https://dj-rest-auth.readthedocs.io/en/latest/installation.html#social-authentication-optional
'''