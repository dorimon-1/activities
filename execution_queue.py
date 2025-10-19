#Written by:
# דניאל קצ'מרק
from collections import deque



class ExecutionQueue:
    """
    FIFO queue for Task objects.
    Tracks total scheduled days and enforces a monthly capacity (default 22).
    """

    def __init__(self, max_days: int = 0):
        """
        Initializes the execution queue.

        Args:
            max_days (int): Maximum days that can be scheduled in the queue.
        """
        self._q = deque()
        self._max_days = max_days
        self._total_days = 0

    @property
    def max_days(self) -> int:
        """Returns the maximum number of days allowed for scheduling."""
        return self._max_days

    @property
    def total_days(self) -> int:
        """Returns the total number of days currently scheduled."""
        return self._total_days

    def capacity_left(self) -> int:
        """
        Returns the remaining days that can be scheduled.

        Returns:
            int: Remaining days.
        """
        return self._max_days - self._total_days

    def __len__(self) -> int:
        """Returns the number of tasks currently in the queue."""
        return len(self._q)

    def as_list(self):
        """
        Returns a list of all tasks in the queue.

        Returns:
            list: Task objects in the queue.
        """
        return list(self._q)

    def contains(self, task_id: int):
        """
        Checks if a task with the given ID is in the queue.

        Args:
            task_id (int): ID of the task.

        Returns:
            bool: True if the task is in the queue, False otherwise.
        """
        return any(t.task_id == task_id for t in self._q)

    def _add_days(self, d: int):
        """
        Adds days to the total scheduled days counter.

        Args:
            d (int): Number of days to add.
        """
        self._total_days += d

    def _sub_days(self, d: int):
        """
        Subtracts days from the total scheduled days counter.
        Ensures total_days does not go below zero.

        Args:
            d (int): Number of days to subtract.
        """
        self._total_days -= d
        if self._total_days < 0:
            self._total_days = 0

    # ----- FIFO operations -----
    def enqueue(self, task) -> tuple[bool, str]:
        """
        Adds a task to the tail of the queue if capacity allows.

        Args:
            task (Task): Task to add.

        Returns:
            tuple: (success (bool), message (str))
        """
        new_task_dur = task.duration
        if self._total_days + new_task_dur > self._max_days:
            return False, "Not enough remaining capacity."
        self._q.append(task)
        self._add_days(new_task_dur)
        return True, "Enqueued."

    def force_enqueue(self, task) -> tuple[bool, str, list]:
        """
        Forcefully adds a task to the queue.
        Removes tasks from the tail if needed to make space.

        Args:
            task (Task): Task to add.

        Returns:
            tuple: (success (bool), message (str), removed_tasks (list))
        """
        removed = []
        new_task_dur = task.duration
        while self._total_days + new_task_dur > self._max_days and self._q:
            r = self._q.pop()  # remove newest first (tail)
            removed.append(r)
            self._sub_days(r.duration)

        if self._total_days + new_task_dur > self._max_days:
            return False, "Not enough capacity even after removing tasks.", removed

        self._q.append(task)
        self._add_days(new_task_dur)
        msg = "Force-enqueued."
        if removed:
            msg += f" Removed {len(removed)} task(s) from queue tail."
        return True, msg, removed

    def dequeue(self):
        """
        Removes and returns the first task in the queue (FIFO).

        Returns:
            Task or None: The removed task, or None if queue is empty.
        """
        if not self._q:
            return None
        t = self._q.popleft()
        self._sub_days(t.duration)
        return t

    def peek(self):
        """
        Returns the first task in the queue without removing it.

        Returns:
            Task or None: The first task, or None if queue is empty.
        """
        return self._q[0] if self._q else None

    def remove_by_id(self, task_id: int) -> bool:
        """
        Removes a specific task from the queue by ID.

        Args:
            task_id (int): ID of the task to remove.

        Returns:
            bool: True if the task was removed, False otherwise.
        """
        for i, t in enumerate(self._q):
            if t.task_id == task_id:
                self._sub_days(t.duration)  # Update the free execution days
                del self._q[i]  # delete the task
                return True
        return False

    def clear(self):
        """
        Clears the queue and resets the total scheduled days counter.
        """
        self._q.clear()
        self._total_days = 0
