from task_status import Status


class Task:
    _id_generator = 100

    def __init__(self, description, priority, duration, status=Status.PENDING):
        self.task_id = Task._id_generator
        Task._id_generator += 1
        self.description = description
        self.priority = priority
        self.duration = duration
        self.status = status

    def __str__(self):
        return (f"Task #{self.task_id}: {self.description} "
                f"(priority: {self.priority}, duration: {self.duration} days)")

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_duration(self):
        return self.duration

    def get_status(self):
        return self.status

    def set_description(self, description: str):
        self.description = description

    def set_priority(self, priority: int):
        self.priority = priority

    def set_duration(self, duration: int):
        self.duration = duration

    def mark_pending(self):
        self.status = Status.PENDING

    def mark_scheduled(self):
        self.status = Status.SCHEDULED

    def mark_completed(self):
        self.status = Status.COMPLETED

    def mark_cancelled(self):
        self.status = Status.CANCELLED

    def mark_delayed(self):
        self.status = Status.DELAYED

    def mark_in_progress(self):
        self.status = Status.IN_PROGRESS
