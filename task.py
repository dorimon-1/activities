class Task:

    _id_generator = 100

    def __init__(self, description, priority, duration):
        self.task_id = Task._id_generator
        Task._id_generator += 1

        self.description = description
        self.priority = priority
        self.duration = duration
        self.next = None

    def __str__(self):
        return (f"Task #{self.task_id}: {self.description} "
                f"(priority: {self.priority}, duration: {self.duration} days)")

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_duration(self):
        return self.duration

    def set_description(self, description: str):
        self.description = description

    def set_priority(self, priority: int):
        self.priority = priority

    def set_duration(self, duration: int):
        self.duration = duration