from EasyTask.constants import PAGE_SIZE
from UserAuth.views import jwt_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer
from .strategy.strategies import TaskFilterStrategy, TaskSortingStrategy
from .strategy.strategy_context import StrategyContext


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


@api_view(['GET'])
@jwt_required
def get_current_tasks(request):
    queryset = Task.objects.filter(user=request.user)

    strategies = [TaskFilterStrategy(), TaskSortingStrategy()]
    context = StrategyContext(strategies=strategies)
    queryset = context.apply_strategies(queryset, request.query_params)

    paginator = PageNumberPagination()
    paginator.page_size = request.query_params.get('page_size', PAGE_SIZE)
    paginated_tasks = paginator.paginate_queryset(queryset, request)

    serializer = TaskSerializer(paginated_tasks, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


'''
https://dj-rest-auth.readthedocs.io/en/latest/installation.html#social-authentication-optional
ideally there should be a task spec, users can maybe add 
- sort criterias
- filters

at front-end level we need pagination for infinite scrolling
'''
