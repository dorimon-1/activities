#Written by:
#  ישראל-חי זליכה
from task_repo_node import TaskNode

class LinkedList:
    """
    Singly linked list to store TaskNode objects.
    Supports insertion at head, removal, searching, and iteration.
    """

    def __init__(self):
        """
        Initializes an empty linked list with "head" set to None.
        """
        self.head = None

    def _as_node(self, item) -> TaskNode:
        """
        Converts a Task object to a TaskNode, or passes through if already a TaskNode.

        Args:
            item (Task or TaskNode): The item to wrap or return.

        Returns:
            TaskNode: The resulting node.
        """
        if isinstance(item, TaskNode):
            return item
        # כאן item הוא Task
        return TaskNode(item)

    def find(self, task_id):
        """
        Searches for a task by its ID in the linked list.

        Args:
            task_id (int): ID of the task to find.

        Returns:
            Task or None: The task if found, else None.
        """
        cur = self.head
        while cur:
            if cur.task.task_id == task_id:
                return cur.task
            cur = cur.next
        return None

    def insert_head(self, item) -> bool:
        """
        Inserts a task or TaskNode at the head of the list (O(1)).
        Prevents duplicates based on task_id.

        Args:
            item (Task or TaskNode): Task or TaskNode to insert.

        Returns:
            bool: True if inserted successfully, False if duplicate.
        """
        node = self._as_node(item)
        if self.find(node.task.task_id):
            return False
        node.next = self.head
        self.head = node
        return True

    def remove(self, task_id) -> bool:
        """
        Removes a task by its ID from the list.

        Args:
            task_id (int): ID of the task to remove.

        Returns:
            bool: True if task was removed, False if not found.
        """
        prev, cur = None, self.head
        while cur:
            if cur.task.task_id == task_id:
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                cur.next = None
                return True
            prev, cur = cur, cur.next
        return False

    def __iter__(self):
        """
        Iterates over TaskNode objects in the list.

        Yields:
            TaskNode: The next node in the list.
        """
        cur = self.head
        while cur:
            yield cur
            cur = cur.next

    def __len__(self):
        """
        Returns the number of nodes in the list.

        Returns:
            int: Count of nodes.
        """
        count, cur = 0, self.head
        while cur:
            count += 1
            cur = cur.next
        return count

    def display(self):
        """
        Prints all tasks in the list to the console.
        """
        cur = self.head
        while cur:
            print("   ", cur.task)
            cur = cur.next
