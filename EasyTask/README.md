grpc server -> poetry run python grpc_server.py
celery worker -> poetry run celery -A EasyTask worker --loglevel=info
django server -> poetry run python manage.py runserver
run subscriber.py main function directly
run redis docker file -> /Users/kirath/PycharmProjects/EasyTask/docker/redis/docker-compose.yaml


command to generate protobuf files - 
1. Navigate to grpc folder
2. run grpc % python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. subscription.proto
3. Navigate to subscription_pb2_grpc.py file and replace import subscription_pb2 as subscription__pb2 with from . import subscription_pb2 as subscription__pb2