#Written by:
#תמיד אבני
from task import Task
from task_status import Status


class CompletedRepository:
    def __init__(self):
        """
        Initializes the CompletedRepository.
        Stores completed tasks in a dictionary with task_id as key and Task object as value.
        """
        self.completed_tasks = {}  # key: task_id, value: Task object

    def add_task(self, task: Task):
        """
        Adds a task to the completed task repository.

        Args:
            task (Task): Task object to add.

        Returns:
            bool: True if task was successfully added, False if the task is not marked as COMPLETED.
        """
        if task.status != Status.COMPLETED:
            return False
            # raise ValueError("Can't add task that isn't completed")
        self.completed_tasks[task.task_id] = task
        return True

    def get_task(self, task_id: int):
        """
        Retrieves a completed task by its ID.

        Args:
            task_id (int): ID of the task to retrieve.

        Returns:
            Task or None: The task object if found, else None.
        """
        return self.completed_tasks.get(task_id, None)

    def remove_task(self, task_id):
        """
        Removes a task from the completed repository.

        Args:
            task_id (int): ID of the task to remove.
        """
        if task_id in self.completed_tasks:
            del self.completed_tasks[task_id]

    def list_all(self):
        """Return a list of all completed tasks"""
        return list(self.completed_tasks.values())
