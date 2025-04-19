from . import subscription_pb2, subscription_pb2_grpc
from ..models import Subscription
from ..serializers import SubscriptionSerializer
from ..enums import Status_enum
import grpc


class SubscriptionService(subscription_pb2_grpc.SubscriptionServiceServicer):
    def UpdateSubscription(self, request, context):
        try:
            subscription_id, status = request.subscription_id.split("::")
            subscription = Subscription.objects.get(subscription_id=subscription_id)
            serializer = SubscriptionSerializer()
            updated_subscription = serializer.update(subscription, {'status': status})
            print(updated_subscription)
            print(f"Streak type: {type(updated_subscription.streak)}, value: {updated_subscription.streak}")
            print(
                f"[gRPC] Returning: message=Subscription {subscription_id} updated, success=True, streak={updated_subscription.streak}")

            return subscription_pb2.SubscriptionResponse(
                success=True,
                message=f"Subscription {subscription_id} updated",
                streak=updated_subscription.streak,
            )

        except Subscription.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Subscription {subscription_id} not found")
            return subscription_pb2.SubscriptionResponse(success=False)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return subscription_pb2.SubscriptionResponse(success=False)
