from . import subscription_pb2
from . import subscription_pb2_grpc

from ..models import Subscription


class SubscriptionService(subscription_pb2_grpc.SubscriptionServiceServicer):
    def UpdateSubscription(self, request, context):
        subscription_id = request.subscription_id
        print(f"[gRPC Server] Received update request for subscription {subscription_id}")

        subscription = Subscription.objects.get_or_create(subscription_id=subscription_id)

        return subscription_pb2.SubscriptionResponse(
            status="success",
            message=f"Subscription updated for subscription {subscription}"
        )
