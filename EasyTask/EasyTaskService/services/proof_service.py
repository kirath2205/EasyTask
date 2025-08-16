from typing import Optional
from django.db import transaction

from ..models import Proof
from .validation_service import ValidationService


class ProofService:
    def __init__(self):
        self.validation_service = ValidationService()

    @transaction.atomic
    def create_proof(self, image_uri: str, milestone=None) -> Proof:
        """Create a new proof and optionally link it to a milestone"""
        return Proof.objects.create(image_uri=image_uri, milestone=milestone)

    def get_proof_by_id(self, proof_id: str) -> Optional[Proof]:
        """Get proof by ID"""
        try:
            return Proof.objects.get(proof_id=proof_id)
        except Proof.DoesNotExist:
            return None

    def validate_proof_against_task(self, proof: Proof, task) -> bool:
        """Validate proof against task requirements"""
        return self.validation_service.validate_image_against_requirements(
            proof.image_uri, task.requirement
        )
