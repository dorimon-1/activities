
from task import Task
from treap_dataset import Treap
from task_repo import Hashtable
from execution_queue import ExecutionQueue
from completed_rep import CompletedRepository
from task_status import Status

CAPACITY_DAYS = 22  # Preset number to be used for the max days we can schedule each month
Added_Priority = 17  # Preset number to be used for the amount of priority we add to each task if they aren't been assigned to execution_queue


class TaskManager:
    def __init__(self): # תמיר אבני
        """
        Initializes the TaskManager with:
        - A hashtable for storing tasks.
        - An execution queue with monthly capacity.
        - A Treap for priority ordering of tasks.
        - A repository for completed tasks.
        """
        self.table = Hashtable()
        self.exec = ExecutionQueue(max_days=CAPACITY_DAYS)
        self.treap = Treap()
        self.completed_tasks = CompletedRepository()


    def init_system(self): # ישראל חי - זליכה
        """
        Resets the TaskManager to its initial empty state.
        All tables, queues, and repositories are cleared.
        """
        self.table = Hashtable()
        self.exec = ExecutionQueue(max_days=CAPACITY_DAYS)
        self.treap = Treap()
        self.completed_tasks = CompletedRepository()

    def add_task(self, task: Task): # תמיר אבני
        """
        Adds a new task to the system.
        Inserts the task into the hashtable and the priority treap.

        Args:
            task (Task): The task object to add.

        Returns:
            bool: True if task was successfully added, False otherwise.
        """
        added_task = self.table.add_task(task)
        if added_task:
            self.treap.insert(task)
        return added_task

    def get_task(self, task_id: int): #  תמיר אבני
        """
        Retrieves a task from the system by its ID.

        Args:
            task_id (int): The ID of the task to retrieve.

        Returns:
            Task or None: The task object if found, else None.
        """
        return self.table.get_task(task_id)

    def remove_task(self, task_id: int): # תמיר אבני/דניאל
        """
        Removes a task from all system repositories: table, treap, and execution queue.

        Args:
            task_id (int): The ID of the task to remove.

        Returns:
            bool: True if any repository removed the task, False if task not found.
        """
        task_to_remove: Task = self.table.get_task(task_id)
        if not task_to_remove:
            return False

        deleted = False

        if self.table.remove_task(task_id):
            deleted = True
        if self.treap.delete_by_id(task_id):
            deleted = True
        if self.exec.remove_by_id(task_id):
            deleted = True

        return deleted

    def update_task(self, task_id, description=None, duration=None, priority=None): # ישראל חי - זליכה
        """
        Updates a task's properties (description, duration, priority).
        If the task is not in the execution queue, updates its priority in the Treap as well.

        Args:
            task_id (int): ID of the task to update.
            description (str, optional): New description.
            duration (int, optional): New duration.
            priority (int, optional): New priority.

        Returns:
            tuple: (bool updated, str message) indicating success and message.
        """
        t = self.table.get_task(task_id)
        if not t:
            return False, "Task not found."

        updated = False
        if description is not None:
            updated |= self.table.update_task(task_id, "description", description)
        if duration is not None:
            updated |= self.table.update_task(task_id, "duration", duration)
        if priority is not None:
            updated |= self.table.update_task(task_id, "priority", priority)
            if not self.exec.contains(task_id):
                self.treap.update_task_priority(task_id, priority)

        return updated, ("Updated successfully" if updated else "Not updated")

    def set_task_status(self, task_id: int, new_status: Status) -> tuple[bool, str]: # תמיר אבני / דניאל
        """
        Changes the status of a task and updates its location in repositories accordingly.

        Args:
            task_id (int): ID of the task to update.
            new_status (Status): New status (PENDING, SCHEDULED, COMPLETED, etc.)

        Returns:
            tuple: (bool success, str message) indicating result.
        """
        t = self.get_task(task_id)
        if not t:
            return False, "Task not found."
        if not isinstance(new_status, Status):
            return False, "Status must be a Status enum."

        old = t.get_status()
        try:
            t.set_status(new_status)
        except TypeError as e:
            return False, str(e)

        if new_status == Status.SCHEDULED:
            ok, msg = self.insert_to_execution_queue(task_id)
            if not ok:
                t.set_status(old)  # rollback
                return False, msg
            self.treap.delete_by_id(task_id)
            return True, "Task scheduled (moved to execution queue)."

        if new_status == Status.PENDING:
            removed = self.exec.remove_by_id(task_id)
            if removed:
                self.treap.insert(removed)
            return True, "Task set to pending (back to priority repository)."

        if new_status == Status.DELAYED:
            return True, "Task marked delayed."

        if new_status == Status.COMPLETED:
            self.exec.remove_by_id(task_id)
            self.treap.delete_by_id(task_id)
            self.table.remove_task(task_id)
            self.completed_tasks.add_task(t)
            return True, "Task completed: archived and removed from all repositories."

        if new_status == Status.CANCELLED:
            self.exec.remove_by_id(task_id)
            self.treap.delete_by_id(task_id)
            self.table.remove_task(task_id)
            return True, "Task cancelled and removed."

        return True, f"Status set to {new_status.name}."

    def insert_to_execution_queue(self, task_id: int): # דניאל /סתיו
        """
        Inserts a task into the execution queue respecting capacity constraints.
        Removes it from Treap while scheduled, keeps it in the table.

        Args:
            task_id (int): Task to schedule.

        Returns:
            tuple: (bool success, str message)
        """
        task = self.get_task(task_id)
        if not task:
            return False, "Task not found."
        if self.exec.contains(task_id):
            return False, "Task already in execution queue."
        ok, msg = self.exec.enqueue(task)
        if not ok:
            return False, "Not enough remaining capacity. Use force insert if needed."
        return True, "Enqueued."

    def force_insert_to_execution_queue(self, task_id: int): # דניאל / סתיו
        """
        Forcefully inserts a task into the execution queue, potentially removing other tasks.
        Removed tasks are returned to the Treap.

        Args:
            task_id (int): Task to force insert.

        Returns:
            tuple: (bool success, str message, list removed_tasks)
        """
        task = self.get_task(task_id)
        if not task:
            return False, "Task not found.", []
        if self.exec.contains(task_id):
            return False, "Task already in execution queue.", []

        ok, msg, removed = self.exec.force_enqueue(task)
        if not ok:
            return False, msg, []

        for r in removed:
            self.treap.insert(r)

        self.treap.delete_by_id(task_id)
        task.set_status(Status.SCHEDULED)
        return True, msg, removed

    def create_priority_queue(self, order="desc"): # דור סהר
        """
        Returns the list of tasks sorted by priority.

        Args:
            order (str): "desc" for descending, "asc" for ascending priority.

        Returns:
            list: Sorted tasks.
        """
        return self.treap.to_list(order=order)

    def print_tasks_by_priority(self): # דור סהר
        """
        Returns a string representation of tasks ordered by priority.

        Returns:
            str: Tasks joined by newline.
        """
        return "\n".join(str(t) for t in self.create_priority_queue())

    @property
    def exec_queue_as_list(self): # דניאל / סתיו
        """
        Returns a list of tasks currently in the execution queue.

        Returns:
            list: Execution queue tasks.
        """
        return self.exec.as_list()

    def completed_tasks_as_list(self): # תמיר אבני
        """
        Returns a list of all completed tasks.

        Returns:
            list: Completed tasks.
        """
        return self.completed_tasks.list_all()

    def close_previous_month(self): # דניאל / סתיו
        """
        Marks all scheduled tasks as completed and clears the execution queue.
        """
        for t in self.exec.as_list():
            self.set_task_status(t.task_id, Status.COMPLETED)
        self.exec.clear()

    def assign_month_simple(self, capacity_days: int = CAPACITY_DAYS): # דניאל / סתיו
        """
        Assigns tasks for the current month until capacity is reached.

        Args:
            capacity_days (int): Maximum days for scheduling.

        Returns:
            tuple: (assigned_tasks, waiting_tasks)
        """
        self.close_previous_month()
        assigned, waiting = [], []
        for t in self.treap.to_list(order="desc"):
            ok, msg = self.set_task_status(t.task_id, Status.SCHEDULED)
            if ok:
                assigned.append(t)
            else:
                waiting.append(t)
        return assigned, waiting

    def system_preset(self): # ישראל חי - זליכה
        """
        Resets the system and loads a predefined set of tasks into the system.
        Resets Task ID generator if necessary.
        """
        self.init_system()
        if Task.id_generator != 100:
            Task._id_generator = 100
        print("System has been reset!")
        print("Adding Preset tasks...")
        tasks = [Task("Component A", 1, 2),
                 Task("Component B", 10, 5),
                 Task("Components C+D", 9, 1),
                 Task("Element Composite 3", 8, 10),
                 Task("Component E", 1, 3),
                 Task("Component F", 2, 3),
                 Task("Component G", 9, 5),
                 Task("New Component G", 10, 8),
                 Task("Simple Element A", 6, 7),
                 Task("Component H", 5, 5),
                 Task("Component J", 2, 5), Task("Element Composite 3", 2, 10),
                 Task("Element Composite 4", 1, 12),
                 Task("Element Composite 5", 3, 18),
                 Task("Component A", 9, 2),
                 Task("Component E", 10, 3),
                 Task("New Component A", 4, 4),
                 Task("Component J - Reversed Steering Repair", 5, 5),
                 Task("Component Paint A", 6, 1),
                 Task("Component Paint A", 7, 1),
                 Task("Component Paint B", 8, 1),
                 Task("Component Paint C", 5, 1),
                 Task("Component A", 3, 2),
                 Task("Component A", 4, 2),
                 Task("Element Composite 3 - faulty", 9, 10),
                 Task("Element 5 - New", 7, 5)]
        for task in tasks:
            self.add_task(task)

        print(f"{len(tasks)} tasks loaded into the system.")


