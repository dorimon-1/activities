from enum import Enum


class Status(Enum): # ישראל חי - זליכה
    """
    Enum representing the status of a task.

    Attributes:
        PENDING: Task is pending and not yet scheduled.
        SCHEDULED: Task has been scheduled in the execution queue.
        COMPLETED: Task has been finished and archived.
        CANCELLED: Task was cancelled and removed.
        DELAYED: Task is delayed but remains in the repository.
    """
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "canceled"
    DELAYED = "delayed"
