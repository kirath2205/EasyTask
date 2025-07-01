from celery import shared_task
from EasyTaskService.business import TaskManager
from EasyTaskService.services import ProofService, SubscriptionService

import traceback


@shared_task
def handle_expiry_event(message):
    """Handle Redis key expiry events"""
    print(f"Processing expiry event: {message}")
    expired_data = message['data'].decode('utf-8')
    print(f"Key expired: {expired_data}")

    subscription_id, status = expired_data.split("::")

    # Use business layer for processing
    task_manager = TaskManager()
    result = task_manager.process_proof_validation(
        proof_id=None,
        subscription_id=subscription_id,
        validation_result=False  # Expired = failed
    )

    return result


@shared_task
def handle_proof_validation(proof_id, subscription_id, task_id):
    """Handle proof validation"""
    print(f"[Celery] Processing proof validation:")
    print(f"  - proof_id: {proof_id}")
    print(f"  - subscription_id: {subscription_id}")
    print(f"  - task_id: {task_id}")

    try:
        # Get proof and subscription
        proof_service = ProofService()
        subscription_service = SubscriptionService()

        proof = proof_service.get_proof_by_id(proof_id)
        subscription = subscription_service.get_subscription_by_id(subscription_id)

        if not proof or not subscription:
            return "Proof or subscription not found"

        # Validate proof against task requirements
        validation_result = proof_service.validate_proof_against_task(proof, subscription.task)

        # Use business layer for processing validation result
        task_manager = TaskManager()
        result = task_manager.process_proof_validation(
            proof_id=proof_id,
            subscription_id=subscription_id,
            validation_result=validation_result
        )

        return result

    except Exception as e:
        print(f"Error in proof validation: {e}")
        print(traceback.format_exc())
        return f"Error: {str(e)}"