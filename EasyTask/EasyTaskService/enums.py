from enum import Enum


class Status_enum(Enum):
    UPCOMING = 'UPCOMING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    OVERDUE = 'OVERDUE'


class Snapshot_status_enum(Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Subscription_enum(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
