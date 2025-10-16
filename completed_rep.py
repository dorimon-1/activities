#Written by:
#תמיד אבני
from task import Task
from task_status import Status


class CompletedRepository:

    def __init__(self):
        self.completed_tasks = {}  # key: task_id, value: Task object

    def add_task(self, task: Task):
        if task.status != Status.COMPLETED:
            return False
            # raise ValueError("Can't add task that isn't completed")
        self.completed_tasks[task.task_id] = task
        return True

    def get_task(self, task_id: int):
        return self.completed_tasks.get(task_id, None)

    def remove_task(self, task_id):
        if task_id in self.completed_tasks:
            del self.completed_tasks[task_id]  # in case of an error

    def list_all(self):
        for task in self.completed_tasks.values():
            print(task)
