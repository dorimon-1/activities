from task import Task


class TaskNode:
    """
    Node wrapper for a Task object used in linked lists.

    Attributes:
        task (Task): The task stored in this node.
        next (TaskNode or None): Reference to the next node in the list.
    """

    def __init__(self, task: Task): # ישראל חי - זליכה
        """
        Initializes a TaskNode with a Task object.

        Args:
            task (Task): Task to store in the node.
        """
        self.task = task
        self.next = None
