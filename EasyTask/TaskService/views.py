from UserAuth.views import jwt_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TaskSerializer


# Create your views here.
@api_view(['POST'])
@jwt_required
def create_task(request):
    task_payload = request.data
    serialized_task = TaskSerializer(data=task_payload, context={'request': request})
    if not serialized_task.is_valid():
        return Response(serialized_task.errors, status=status.HTTP_400_BAD_REQUEST)

    saved_task = serialized_task.save()
    return Response({'message': f'Task {saved_task.task_id} created successfully'}, status=status.HTTP_201_CREATED)

'''
https://dj-rest-auth.readthedocs.io/en/latest/installation.html#social-authentication-optional
'''
