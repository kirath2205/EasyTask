import grpc
from celery import shared_task
from EasyTaskService.grpc import subscription_pb2, subscription_pb2_grpc
import traceback

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
            print(f"[Celery] gRPC response: {response.success} - {response.message}")
    except grpc.RpcError as e:
        print(f"[Celery] gRPC failed: code={e.code()}, details={e.details()}")
    except Exception as e:
        traceback.print_exc()
        print(f"[Celery] Unknown error in gRPC call: {e}")

