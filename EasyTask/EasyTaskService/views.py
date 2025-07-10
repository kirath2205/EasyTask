from rest_framework.response import Response
import traceback

from EasyTask.celery import app
from UserAuth.views import jwt_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from .business import TaskManager
from .exceptions import PermissionException
from .serializers import PublicSubscriptionSerializer, TaskSerializer, ProofSerializer, SubscriptionSerializer, MilestoneSerializer
from .services import SubscriptionService


@api_view(['POST'])
@jwt_required
def create_private_task(request):
    serializer = TaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task_manager = TaskManager()
    result = task_manager.create_user_task(request.user, serializer.validated_data)

    if result['success']:
        return Response({
            'message': result['message'],
            'subscription_id': result['subscription_id'],
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@jwt_required
def create_public_task(request):
    """
    :param request:
    :return:
    """
    serializer = TaskSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task_manager = TaskManager()
    result = task_manager.create_public_task(request.user, serializer.validated_data)

    if result['success']:
        return Response({
            'message': result['message'],
            'task_id': result['task_id'],
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@jwt_required
def subscribe_task(request):
    serializer = PublicSubscriptionSerializer(request.data).data

    if not serializer:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task_manager = TaskManager()
    result = task_manager.create_subscription(request.user, serializer.get("task_id"))

    if result['success']:
        return Response({
            'message': result['message'],
            'subscription_id': result['subscription_id'],
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@jwt_required
def get_subscriptions(request):
    """
    Get user subscriptions using service layer
    """
    user = request.user
    subscription_status = request.query_params.get('status', None)
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))

    try:
        subscription_service = SubscriptionService()
        result = subscription_service.get_subscriptions_paginated(
            user=user, status=subscription_status, page=page, page_size=page_size
        )

        # Serialize the results
        serialized_results = SubscriptionSerializer(result['results'], many=True).data

        return Response({
            'results': serialized_results,
            'count': result['count'],
            'next': result['next'],
            'previous': result['previous']
        })

    except Exception as e:
        print(f"Error getting subscriptions: {e}")
        print(traceback.format_exc())
        return Response({"error": "Something went wrong. Please try again later."}, status=500)


@api_view(['POST'])
@jwt_required
def submit_proof(request):
    """
    Submit proof using business layer
    """
    serializer = ProofSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Use business layer for proof submission
    task_manager = TaskManager()
    result = task_manager.submit_task_proof(
        subscription_id=str(serializer.validated_data['subscription_id']),
        image_uri=serializer.validated_data['image_uri']
    )

    if not result['success']:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Trigger async validation
        app.send_task('TaskProcessor.tasks.handle_proof_validation',
                      args=[result['proof_id'], result['subscription_id'], result['task_id']])

        return Response({
            'message': result['message'],
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'message': "Could not submit proof. Please try again"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@jwt_required
def get_milestone(request):
    try:
        subscription_id = request.query_params.get('subscription_id', None)
        task_manager = TaskManager()
        milestone = task_manager.get_milestone(user=request.user, subscription_id=subscription_id)

        if not milestone:
            return Response({
                'error': f"milestone for subscription id {subscription_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        serialized_milestone = MilestoneSerializer(milestone).data
        return Response({
            'data': serialized_milestone
        })
    except PermissionException.PermissionException as e:
        return Response({"error": e.message}, status=HTTP_403_FORBIDDEN)

    except Exception as e:
        print(f"Error getting milestone for subscription: {subscription_id} {e}")
        print(traceback.format_exc())
        return Response({"error": f"Error getting milestone for subscription: {subscription_id} {e}"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
