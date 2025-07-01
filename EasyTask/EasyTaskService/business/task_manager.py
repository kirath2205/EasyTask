from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model

from ..services import TaskService, SubscriptionService, ProofService
from ..models import Subscription

User = get_user_model()


class TaskManager:
    """
    Business logic layer for task management
    Orchestrates multiple services to implement business workflows
    """

    def __init__(self):
        self.task_service = TaskService()
        self.subscription_service = SubscriptionService()
        self.proof_service = ProofService()

    def create_user_task(self, user: User, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Business workflow for creating a user task
        """
        try:
            subscription = self.task_service.create_private_task(user, task_data)
            return {
                'success': True,
                'subscription_id': str(subscription.subscription_id),
                'message': 'Private task created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create task'
            }

    def submit_task_proof(self, subscription_id: str, image_uri: str) -> Dict[str, Any]:
        """
        Business workflow for submitting task proof
        """
        try:
            # Get subscription
            subscription = self.subscription_service.get_subscription_by_id(subscription_id)
            if not subscription:
                return {
                    'success': False,
                    'error': 'Subscription not found'
                }

            # Create proof
            proof = self.proof_service.create_proof(image_uri)

            # Return data for async processing
            return {
                'success': True,
                'proof_id': str(proof.proof_id),
                'subscription_id': subscription_id,
                'task_id': str(subscription.task.task_id),
                'message': 'Proof submitted for validation'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to submit proof'
            }

    def process_proof_validation(self, proof_id: str, subscription_id: str,
                                 validation_result: bool) -> Dict[str, Any]:
        """
        Business workflow for processing proof validation results
        """
        try:
            subscription = self.subscription_service.get_subscription_by_id(subscription_id)

            if not subscription:
                return {
                    'success': False,
                    'error': 'Subscription not found'
                }
            proof = None
            if proof_id is not None:
                proof = self.proof_service.get_proof_by_id(proof_id)
            # Determine status based on validation
            status = 'COMPLETED' if validation_result else 'FAILED'

            # Update subscription
            updated_subscription = self.subscription_service.update_subscription_status(
                subscription, status, proof if validation_result else None
            )

            return {
                'success': True,
                'subscription_id': subscription_id,
                'status': updated_subscription.status,
                'streak': updated_subscription.streak,
                'message': f'Subscription updated with status: {status}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process validation'
            }