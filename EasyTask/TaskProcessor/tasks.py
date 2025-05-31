from celery import shared_task
from EasyTaskService.serializers import SubscriptionSerializer
from EasyTaskService.models import Proof, Subscription

import traceback

from EasyTaskService.enums import Status_enum


@shared_task
def handle_expiry_event(message):
    print(f"Processing a new task {message}")
    expired_data = message['data'].decode('utf-8')
    print(f"Key expired: {expired_data}")
    subscription_id, status = expired_data.split("::")
    print(subscription_workflow(subscription_id=subscription_id, status=status))


@shared_task
def handle_proof_validation(proof_id, subscription_id, task_id):
    print(f"[Celery] proof is {subscription_id}")
    print(f"[Celery] subscription_id is {subscription_id}")
    print(f"[Celery] task id is {task_id}")
    print(subscription_workflow(subscription_id=subscription_id, proof_id=proof_id))


def validate_image(image_uri, task):
    '''
            Make LLM call here, if the proof passes, create a new proof resource and link it to subscription

        '''
    '''
    Validate requirement
    '''
    print(f"Validating {task}")
    return True


def subscription_workflow(subscription_id, proof_id=None, status=None):
    try:
        subscription = Subscription.objects.get(subscription_id=subscription_id)
        proof = None
        if proof_id:
            proof = Proof.objects.get(proof_id=proof_id)
        if proof:
            image_validated = _validate_image(proof.image_uri, subscription)
            if not image_validated:
                return "Verification failed"
            status = Status_enum.COMPLETED

        subscription = Subscription.objects.get(subscription_id=subscription_id)
        serializer = SubscriptionSerializer()
        updated_subscription = serializer.update(subscription, {'status': status}, proof)
        print(updated_subscription)
        print(f"Streak type: {type(updated_subscription.streak)}, value: {updated_subscription.streak}")
        print(
            f"[gRPC] Returning: message=Subscription {subscription_id} updated, success=True, streak={updated_subscription.streak}")

        return f"Subscription {subscription_id} updated"

    except Subscription.DoesNotExist:
        return 'Subscription does not exist'

    except Exception as e:
        return str(e.__str__())


def _validate_image(image_uri, subscription):
    '''
                Make LLM call here, if the proof passes, create a new proof resource and link it to subscription

        '''
    '''
    Validate requirement
    '''
    task = subscription.get_task()
    print(f"Validating {task.requirement}")
    return True
