from django.core.cache.backends import redis
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from UserAuth.views import jwt_required
from .serializers import PrivateTaskSerializer
from EasyTask.settings import redis_client


@api_view(['POST'])
@jwt_required
def create_private_task(request):
    serialized_task = PrivateTaskSerializer(data=request.data, context={'request': request})
    if not serialized_task.is_valid():
        return Response(serialized_task.errors, status=status.HTTP_400_BAD_REQUEST)

    subscription = serialized_task.save()

    return Response({
        'message': 'Private task created successfully',
        'subscription_id': subscription.subscription_id,
    },
        status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_redis(request):
    try:
        pong = redis_client.ping()
        return Response({'message': f"✅ Redis is running: {pong}"})
    except redis.exceptions.ConnectionError as e:
        return Response({'message': f"❌ Redis connection error: {e}"})
