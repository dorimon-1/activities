#Written by:
#תמיד אבני +ישראל-חי זליכה
from task import Task
from treap_dataset import Treap
from task_repo import Hashtable
from execution_queue import ExecutionQueue
from completed_rep import CompletedRepository
from task_status import Status

CAPACITY_DAYS = 22  # Preset number to be used for the max days we can schedule each month
Added_Priority = 17  # Preset number to be used for the amount of priority we add to each task if they aren't been assigned to execution_queue


class TaskManager:
    def __init__(self):
        self.table = Hashtable()
        self.exec = ExecutionQueue(max_days=CAPACITY_DAYS)
        self.treap = Treap()
        self.completed_tasks = CompletedRepository()


    def init_system(self):
        self.table = Hashtable()
        self.exec = ExecutionQueue(max_days=CAPACITY_DAYS)
        self.treap = Treap()
        self.completed_tasks = CompletedRepository()


    def add_task(self, task: Task):
        """Adding a task to the tasks table and to the priority queue"""
        added_task = self.table.add_task(task)
        if added_task:
            self.treap.insert(task)
        return added_task

    def get_task(self, task_id: int):
        return self.table.get_task(task_id)

    def remove_task(self, task_id: int):
        """Removing a task from the tasks table"""
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

    def update_task(self, task_id, description=None, duration=None, priority=None):
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
            # sync treap priority only if task is not currently in exec queue:
            if not self.exec.contains(task_id):
                self.treap.update_task_priority(task_id, priority)

        return updated, ("Updated successfully" if updated else "Not updated")

    def set_task_status(self, task_id: int, new_status: Status) -> tuple[bool, str]:
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
            # while scheduled, it must not be in treap
            self.treap.delete_by_id(task_id)
            return True, "Task scheduled (moved to execution queue)."

        if new_status == Status.PENDING:
            removed = self.exec.remove_by_id(task_id)
            if removed:
                self.treap.insert(removed)
            return True, "Task set to pending (back to priority repository)."

        if new_status == Status.DELAYED:
            # purely display status, no repo moves
            return True, "Task marked delayed."

        if new_status == Status.COMPLETED:
            # remove from all operational repos and archive
            self.exec.remove_by_id(task_id)
            self.treap.delete_by_id(task_id)
            self.table.remove_task(task_id)
            self.completed_tasks.add_task(t)
            return True, "Task completed: archived and removed from all repositories."

        if new_status == Status.CANCELLED:
            # design choice: remove without archiving
            self.exec.remove_by_id(task_id)
            self.treap.delete_by_id(task_id)
            self.table.remove_task(task_id)
            return True, "Task cancelled and removed."

        return True, f"Status set to {new_status.name}."

        # -------- helpers --------

    def insert_to_execution_queue(self, task_id: int) -> tuple[bool, str]:
        """
        Insert a task to the execution queue (respects monthly capacity).
        Removes the task from the Treap while it is scheduled,
        keeps it in the Hashtable, and updates task-state flags.
        Returns: (ok, message)
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

    def force_insert_to_execution_queue(self, task_id: int) -> tuple[bool, str, list]:
        task = self.get_task(task_id)
        if not task:
            return False, "Task not found.", []
        if self.exec.contains(task_id):
            return False, "Task already in execution queue.", []

        ok, msg, removed = self.exec.force_enqueue(task)
        if not ok:
            return False, msg, []

        # removed tasks return to treap (status left as-is unless you decide otherwise)
        for r in removed:
            self.treap.insert(r)

        self.treap.delete_by_id(task_id)
        # enforce status centrally (now it's scheduled)
        task.set_status(Status.SCHEDULED)
        return True, msg, removed

    def create_priority_queue(self, order="desc"):
        """
        מחזיר רשימה של המשימות לפי עדיפות.
        כברירת מחדל: מהגבוה לנמוך ('desc') כדי לשקף ערימת-מקס.
        """
        return self.treap.to_list(order=order)

    def print_tasks_by_priority(self):
        return "\n".join(str(t) for t in self.create_priority_queue())

    @property
    def exec_queue_as_list(self):
        """This function calls the function in execution repo"""
        return self.exec.as_list()

    def completed_tasks_as_list(self):
        """This function calls the function in complete class to print all completed tasks"""
        return self.completed_tasks.list_all()

    # -------- monthly processes --------
    def close_previous_month(self):
        # mark all scheduled tasks as completed via the central API
        for t in self.exec.as_list():
            self.set_task_status(t.task_id, Status.COMPLETED)
        self.exec.clear()

    def assign_month_simple(self, capacity_days: int = CAPACITY_DAYS):
        self.close_previous_month()
        assigned, waiting = [], []
        for t in self.treap.to_list(order="desc"):
            ok, msg = self.set_task_status(t.task_id, Status.SCHEDULED)
            if ok:
                assigned.append(t)
            else:
                waiting.append(t)
        return assigned, waiting

    def system_preset(self):
        """This function is performing a reset to all classes and tables
         and then adds preset tasks to the system."""
        self.init_system()  # Run init fun that resets all classes and lists
        print("System has been reset!")
        print("Adding Preset tasks...")
        tasks = [
            Task("Component A", 1, 2),
            Task("Component B", 10, 5),
            Task("Components C+D", 9, 1),
            Task("Element Composite 3", 8, 10),
            Task("Component E", 1, 3),
            Task("Component F", 2, 3),
            Task("Component G", 9, 5),
            Task("New Component G", 10, 8),
            Task("Simple Element A", 6, 7),
            Task("Component H", 5, 5),
            Task("Component J", 2, 5),
            Task("Element Composite 3", 2, 10),
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
            Task("Element 5 - New", 7, 5)
        ]
        for task in tasks:
            self.add_task(task)

        print(f"{len(tasks)} tasks loaded into the system.")

    def reset_system(self):
        """
        Resets the TaskManager system to its initial state (like system_preset).
        """

        self.table = Hashtable()
        self.exec = ExecutionQueue(max_days=CAPACITY_DAYS)
        self.treap = Treap()
        self.completed_tasks = CompletedRepository()
        self.system_preset()

        print("System has been reset to initial state.")
