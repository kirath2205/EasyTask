import grpc
from concurrent import futures
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EasyTask.settings")
django.setup()

from EasyTaskService.grpc.service import SubscriptionService
from EasyTaskService.grpc import subscription_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    subscription_pb2_grpc.add_SubscriptionServiceServicer_to_server(SubscriptionService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server listening on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
