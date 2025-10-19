#Written by:
#תמיד אבני
from task_status import Status

class Task:
    """
    Represents a task with a unique ID, description, priority, duration, and status.
    ID is auto-generated starting from 100.
    """

    _id_generator = 100

    def __init__(self, description, priority, duration, status=Status.PENDING):
        """
        Initializes a Task object.

        Args:
            description (str): Description of the task.
            priority (int): Priority of the task.
            duration (int): Duration of the task in days.
            status (Status, optional): Initial status of the task. Defaults to Status.PENDING.
        """
        self.task_id = Task._id_generator
        Task._id_generator += 1
        self.description = description
        self.priority = priority
        self.duration = duration
        self._status = None
        self.set_status(status)  # Validate and set status

    def __str__(self):
        """
        Returns a string representation of the task.

        Returns:
            str: Task info with ID, description, priority, duration, and status.
        """
        return (f"Task #{self.task_id}: {self.description} "
                f"(priority: {self.priority}, duration: {self.duration} days, status: {self.status.name})")

    def get_description(self):
        """Returns the task description."""
        return self.description

    def get_priority(self):
        """Returns the task priority."""
        return self.priority

    def get_duration(self):
        """Returns the task duration in days."""
        return self.duration

    def get_status(self):
        """Returns the task status."""
        return self._status

    def set_description(self, description: str):
        """
        Updates the task description.

        Args:
            description (str): New description.
        """
        self.description = description

    def set_priority(self, priority: int):
        """
        Updates the task priority.

        Args:
            priority (int): New priority value.
        """
        self.priority = priority

    def set_duration(self, duration: int):
        """
        Updates the task duration.

        Args:
            duration (int): New duration in days.
        """
        self.duration = duration

    # ----- status (Enum-only) -----
    @property
    def status(self) -> Status:
        """Returns the task status (getter for property)."""
        return self._status

    @status.setter
    def status(self, value: Status):
        """
        Sets the task status via property setter.

        Args:
            value (Status): Status enum to set.
        """
        self.set_status(value)

    def set_status(self, status: Status):
        """
        Validates and sets the task status.

        Args:
            status (Status): Status enum to set.

        Raises:
            TypeError: If status is not a Status enum.
        """
        if not isinstance(status, Status):
            raise TypeError("status must be a Status enum")
        self._status = status

    @property
    def id_generator(self):
        """Returns the current value of the class-level ID generator."""
        return self._id_generator

