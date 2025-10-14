from task import Task


class TaskNode:
    def __init__(self, task: Task):
        self.task = task
        self.next = None
