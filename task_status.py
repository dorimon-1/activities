#Written by:
#  ישראל-חי זליכה
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "canceled"
    DELAYED = "delayed"
