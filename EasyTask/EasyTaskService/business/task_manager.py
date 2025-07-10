from typing import Any, Dict

from django.contrib.auth import get_user_model

from ..exceptions.PermissionException import PermissionException
from ..services import MilestoneService, ProofService, SubscriptionService, TaskService

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
        self.milestone_service = MilestoneService()

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

    def create_public_task(self, user: User, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
            Business workflow for creating a brand task
        """
        try:
            task = self.task_service.create_public_task(user, task_data)
            return {
                'success': True,
                'task_id': str(task.task_id),
                'message': 'Brand task created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create brand task'
            }

    def create_subscription(self, user: User, task_id) -> Dict[str, Any]:
        try:
            task = self.task_service.get_task_by_id(task_id=task_id)
            subscription = self.task_service.create_subscription(user, task)
            return {
                'success': True,
                'subscription_id': str(subscription.subscription_id),
                'message': 'Subscribed successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Subscription failed'
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

            milestone = self.milestone_service.get_active_milestone(subscription)
            if milestone is None:
                return {
                    'success': False,
                    'error': 'No active milestone',
                }

            elif milestone.is_completed:
                return {
                    'success': False,
                    'error': 'Latest milestone has already been completed',
                }

            # Create proof linked to milestone
            proof = self.proof_service.create_proof(image_uri, milestone=milestone)

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

    def get_milestone(self, user: User, subscription_id: str):
        subscription = self.subscription_service.get_subscription_by_id(subscription_id)

        if subscription.status == "COMPLETED":
            return {
                "status": subscription.status
            }

        if not user == subscription.user:
            raise PermissionException("User does not have access to this subscription")

        milestone = self.milestone_service.get_active_or_future_milestone(subscription)

        return milestone
