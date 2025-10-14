from collections import deque

class ExecutionQueue:
    """
    FIFO queue of Task objects.
    Tracks total scheduled days and enforces a monthly capacity (default 22).
    """

    def __init__(self, max_days: int = 22):
        self._q = deque()
        self._max_days = max_days
        self._total_days = 0

    @property
    def max_days(self) -> int:
        """Read only parameter - shows how much days can be scheduled """
        return self._max_days

    @property
    def total_days(self) -> int:
        """Read only parameter - shows how many days are already scheduled """
        return self._total_days

    def capacity_left(self) -> int:
        """Read only parameter - shows how much days are left to be scheduled """
        return self._max_days - self._total_days

    def __len__(self) -> int:
        """Shows how much tasks are scheduled by length of the queue """
        return len(self._q)

    def as_list(self):
        """Shows the list of scheduled tasks"""
        return list(self._q)

    def contains(self, task_id: int):
        """Check if a task is scheduled by id, Returns - Boolean """
        return any(t.task_id == task_id for t in self._q)

    def _add_days(self, d: int):
        """Add days to 'total_days' to keep a counter of O(1) and not to count every time O(n)"""
        self._total_days += d

    def _sub_days(self, d: int):
        """Subtract days from 'total_days' to keep a counter of O(1) and not to count every time O(n)"""
        self._total_days -= d
        if self._total_days < 0:
            self._total_days = 0

    # ----- FIFO ops -----
    def enqueue(self, task) -> tuple[bool, str]:
        """Add task to tail if capacity allows. Returns (ok, msg)."""
        new_task_dur = task.duration
        if self._total_days + new_task_dur > self._max_days:
            return False, "Not enough remaining capacity."
        self._q.append(task)
        self._add_days(new_task_dur)
        return True, "Enqueued."

    def force_enqueue(self, task) -> tuple[bool, str, list]:
        """
        Append to tail, Removes tasks from tail until there is room.
        Removal from tail preserves FIFO among the remaining tasks.
        Returns (ok, msg, removed_tasks)
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
        """Pop from head (FIFO)."""
        if not self._q:
            return None
        t = self._q.popleft()
        self._sub_days(t.duration)
        return t

    def peek(self):
        return self._q[0] if self._q else None

    def remove_by_id(self, task_id: int):
        """Remove a specific task by id anywhere in the queue. Returns the removed task or None."""
        if not self._q:
            return None
        tmp = deque()
        removed = None
        while self._q:
            t = self._q.popleft()
            if removed is None and t.task_id == task_id:
                removed = t
                self._sub_days(t.duration)
            else:
                tmp.append(t)
        self._q = tmp
        return removed

    def clear(self):
        """Used to clear the execution using generic function and reverting the 'total_days' to 0 """
        self._q.clear()
        self._total_days = 0
