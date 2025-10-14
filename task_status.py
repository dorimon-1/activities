from enum import Enum


class Status(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"
    IN_PROGRESS = "in progress"

