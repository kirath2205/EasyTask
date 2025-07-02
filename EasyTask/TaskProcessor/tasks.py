import traceback

from celery import shared_task

from EasyTaskService.business import TaskManager
from EasyTaskService.services import ProofService
from EasyTaskService.services import SubscriptionService


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