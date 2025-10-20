from task import Task
from linked_list_buckets import LinkedList


class Hashtable:
    """
    A hash table implementation for storing Task objects.
    Uses separate chaining with linked lists for collision handling.
    Supports dynamic resizing (rehash) when load factor is high.
    """

    def __init__(self, capacity=50): # תמיר אבני
        """
        Initializes the hash table.

        Args:
            capacity (int): Initial number of buckets. Minimum 1.
        """
        self.capacity = max(1, capacity)
        self.table = [LinkedList() for _ in range(self.capacity)]

    def _hash_func(self, task_id): # תמיר אבני
        """
        Computes the hash index for a task ID.

        Args:
            task_id (int): Task ID to hash.

        Returns:
            int: Bucket index.
        """
        return task_id % self.capacity

    def _rehash(self): # ישראל חי - זליכה
        """
        Doubles the table capacity and redistributes tasks.
        This is called when the load factor exceeds a threshold.
        """
        old_table = self.table
        self.capacity *= 2
        self.table = [LinkedList() for _ in range(self.capacity)]

        for bucket in old_table:
            cur = bucket.head
            while cur:
                next_node = cur.next
                cur.next = None
                idx = self._hash_func(cur.task.task_id)
                self.table[idx].insert_head(cur)
                cur = next_node

    def add_task(self, task: Task) -> bool: # תמיר אבני
        """
        Adds a task to the hash table.
        Performs rehash if the load factor is too high.

        Args:
            task (Task): Task to add.

        Returns:
            bool: True if task was added, False if duplicate.
        """
        if len(self) / self.capacity > 2:
            self._rehash()

        idx = self._hash_func(task.task_id)
        return self.table[idx].insert_head(task)

    def get_task(self, task_id): # תמיר אבני
        """
        Retrieves a task by its ID.

        Args:
            task_id (int): ID of the task to find.

        Returns:
            Task or None: Task if found, else None.
        """
        idx = self._hash_func(task_id)
        return self.table[idx].find(task_id)

    def remove_task(self, task_id) -> bool: # תמיר אבני
        """
        Removes a task by its ID.

        Args:
            task_id (int): ID of the task to remove.

        Returns:
            bool: True if task was removed, False otherwise.
        """
        idx = self._hash_func(task_id)
        return self.table[idx].remove(task_id)

    def update_task(self, task_id, field: str, new_value) -> bool: # ישראל חי - זליכה
        """
        Updates a field of a task.

        Args:
            task_id (int): ID of the task to update.
            field (str): Field name ("description", "priority", "duration").
            new_value: New value to set.

        Returns:
            bool: True if update succeeded, False if task not found or invalid field.
        """
        t = self.get_task(task_id)
        if not t:
            return False
        if field == "description":
            t.set_description(str(new_value))
        elif field == "priority":
            t.set_priority(int(new_value))
        elif field == "duration":
            t.set_duration(int(new_value))
        else:
            return False
        return True

    def __len__(self): # תמיר אבני
        """
        Returns the total number of tasks in the hash table.

        Returns:
            int: Count of tasks.
        """
        return sum(len(bucket) for bucket in self.table)

    def display(self): # ישראל חי - זליכה
        """
        Prints the contents of all non-empty buckets.
        """
        for i, bucket in enumerate(self.table):
            if len(bucket) > 0:
                print(f"Bucket {i}:")
                bucket.display()



