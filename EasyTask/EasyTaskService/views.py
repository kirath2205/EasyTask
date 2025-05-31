from django.core.cache.backends import redis
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from UserAuth.views import jwt_required
from .serializers import PrivateTaskSerializer, ProofSerializer, SubscriptionSerializer
from .models import Task,Subscription
from EasyTask.settings import redis_client
from rest_framework.exceptions import ValidationError
from EasyTask.celery import app
import traceback


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
@jwt_required
def get_subscriptions(request):
    user = request.user
    subscription_status = request.query_params.get('status', None)
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    try:
        subscriptions = SubscriptionSerializer.filter_subscriptions(
            user=user, status=subscription_status, page=page, page_size=page_size, request=request)
        return subscriptions
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        return Response({"error": "Something went wrong. Please try again later."}, status=500)


@api_view(['POST'])
@jwt_required
def submit_proof(request):
    serialized_proof = ProofSerializer(data=request.data)
    if not serialized_proof.is_valid():
        return Response(serialized_proof.errors, status=status.HTTP_400_BAD_REQUEST)

    proof = serialized_proof.save()
    subscription_id = serialized_proof.get_subscription_id()
    print(f"subscription id is {subscription_id}")
    subscription = Subscription.objects.get(subscription_id=subscription_id)
    task = subscription.get_task()

    try:
        app.send_task('TaskProcessor.tasks.handle_proof_validation', args=[proof.proof_id, subscription.subscription_id, task.task_id])

        return Response({
            'message': 'Proof validation in progress',
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'message': "could not submit proof. Please try again"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_redis(request):
    try:
        pong = redis_client.ping()
        return Response({'message': f"✅ Redis is running: {pong}"})
    except redis.exceptions.ConnectionError as e:
        return Response({'message': f"❌ Redis connection error: {e}"})
