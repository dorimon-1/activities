#Written by:
#תמיד אבני
from task_status import Status

class Task:
    _id_generator = 100

    def __init__(self, description, priority, duration, status=Status.PENDING):
        self.task_id = Task._id_generator
        Task._id_generator += 1
        self.description = description
        self.priority = priority
        self.duration = duration
        self._status = None
        self.set_status(status)  # יעבור דרך הולידציה

    def __str__(self):
        return (f"Task #{self.task_id}: {self.description} "
                f"(priority: {self.priority}, duration: {self.duration} days, status: {self.status.name})")

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_duration(self):
        return self.duration

    def get_status(self):
        return self._status

    def set_description(self, description: str):
        self.description = description

    def set_priority(self, priority: int):
        self.priority = priority

    def set_duration(self, duration: int):
        self.duration = duration

    # ----- status (Enum-only) -----
    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Status):
        self.set_status(value)

    def set_status(self, status: Status):
        if not isinstance(status, Status):
            raise TypeError("status must be a Status enum")
        self._status = status
