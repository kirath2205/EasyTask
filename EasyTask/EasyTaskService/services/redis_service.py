from datetime import datetime
from EasyTask.settings import redis_client
from ..enums import Status_enum


class RedisService:
    def __init__(self):
        self.client = redis_client

    def set_subscription_expiry(self, subscription_id: str, due_date: datetime):
        """Set subscription expiry in Redis"""
        due_date_epoch_time = int(due_date.timestamp())
        key = f"{subscription_id}::{Status_enum.IN_PROGRESS.value}"
        self.client.set(key, '', exat=due_date_epoch_time)

    def delete_subscription_expiry(self, subscription_id: str):
        """Delete subscription expiry from Redis"""
        key = f"{subscription_id}::{Status_enum.IN_PROGRESS.value}"
        self.client.delete(key)

    def test_connection(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except Exception:
            return False

