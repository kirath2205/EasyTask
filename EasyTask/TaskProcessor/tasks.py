import grpc
from celery import shared_task
from EasyTaskService.grpc import subscription_pb2, subscription_pb2_grpc


@shared_task
def handle_expiry_event(message):
    print(f"Processing a new task {message}")
    expired_data = message['data'].decode('utf-8')
    print(f"Key expired: {expired_data}")

    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = subscription_pb2_grpc.SubscriptionServiceStub(channel)
            request = subscription_pb2.SubscriptionRequest(subscription_id=expired_data)
            response = stub.UpdateSubscription(request)
            print(f"[Celery] gRPC response: {response.status} - {response.message}")
    except Exception as e:
        print(f"[Celery] Failed to make gRPC call: {e}")
