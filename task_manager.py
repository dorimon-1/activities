from menu import CAPACITY_DAYS, Added_Priority
from task import Task
from treap_dataset import Treap
from hashtable_dataset import Hashtable

class TaskManager:
    def __init__(self):
        self.table = Hashtable()
        self.exec_queue = []
        self.treap = Treap()
        self.task_state = {}  # {task_id: {"deferred": bool, "rejected": bool, "done": bool, "last_priority": int}}
        self.archive_done = set()  # ids שבוצעו
        self.archive_rejected = set()  # ids שנדחו

    def init_system(self):
        self.table = Hashtable()
        self.exec_queue = []
        self.treap = Treap()
        self.task_state = {}  # {task_id: {"deferred": bool, "rejected": bool, "done": bool, "last_priority": int}}
        self.archive_done = set()  # ids שבוצעו
        self.archive_rejected = set()  # ids שנדחו

    def add_task(self, task: Task):
        added_task = self.table.add_task(task)
        if added_task:
            self.treap.insert(task)
        return added_task

    def remove_task(self, task_id: int):
        task_to_remove = self.table.get_task(task_id)
        if not task_to_remove:
            return False
        delete_hash = self.table.remove_task(task_id)
        return delete_hash

    def get_task(self, task_id: int):
        return self.table.get_task(task_id)

    def update_task(self, task_id, description=None, duration=None, priority=None):
        task = self.table.get_task(task_id)
        if not task:
            return False, "Task not found..."
        updated = False

        if description is not None:
            updated |= self.table.update_task(task_id, "description", description)
        if duration is not None:
            updated |= self.table.update_task(task_id, "duration", duration)
        if priority is not None:
            updated |= self.table.update_task(task_id, "priority", priority)
            # להביא שוב את האובייקט (העדיפות כבר עודכנה) ולהכניס חזרה ל־Treap
            self.treap.update_task_priority(task_id, priority)

        return updated, ("Updated successfully" if updated else "Not updated")

    def create_priority_queue(self, order="desc"):
        """
        מחזיר רשימה של המשימות לפי עדיפות.
        כברירת מחדל: מהגבוה לנמוך ('desc') כדי לשקף ערימת-מקס.
        """
        return self.treap.to_list(order=order)

    def close_previous_month(self):
        """מסמן את משימות החודש הקודם כ-DONE ומשחרר את התור, בלי למחוק מה-Hashtable."""
        if not self.exec_queue:
            return
        for t in self.exec_queue:
            self._set_state(t.task_id, done=True, in_exec=False)
            # שים לב: לא מוחקים מ-Hashtable; הן נשארות במאגר הכללי כ'היסטוריה'
            # וגם אינן ב-Treap (הוסר בעת השיבוץ), שזה תקין — הן כבר בוצעו.
        self.exec_queue.clear()

    def assign_month_simple(self, capacity_days: int = CAPACITY_DAYS):
        """
        1) סוגר חודש קודם (מסמן done, לא מוחק מה-Hashtable)
        2) בוחר משימות לשיבוץ לפי עדיפות (גבוה->נמוך), מדלג על done/rejected/in_exec
        3) משובצות: נכנסות לתור הביצוע + יוצאות מה-Treap + נשארות ב-Hashtable
        4) היתר: מסומנות 'ממתינות' (deferred=True) עד אישור/דחייה
        """
        # 1) סגירת חודש קודם
        self.close_previous_month()

        # 2) בחירה לפי עדיפויות
        ordered = self.treap.to_list(order="desc")
        total = 0
        assigned, waiting = [], []

        for t in ordered:
            st = self.task_state.get(t.task_id, {})
            if st.get("done") or st.get("rejected") or st.get("in_exec"):
                continue
            if total + t.duration <= capacity_days:
                assigned.append(t);
                total += t.duration
            else:
                waiting.append(t)

        # 3) משובצות: לתור + הסרה מה-Treap + נשארות ב-Hashtable
        for t in assigned:
            self.exec_queue.append(t)
            self.treap.delete_by_id(t.task_id)  # יוצא ממאגר העדיפויות
            self.set_state(t.task_id, in_exec=True, deferred=False, done=False, last_priority=t.priority)

        # 4) ממתינות: רק סימון (אישור/דחייה בשלב נפרד)
        for t in waiting:
            self.set_state(t.task_id, deferred=True, in_exec=False, done=False, last_priority=t.priority)

        return assigned, waiting

    def set_state(self, task_id, **flags):
        s = self.task_state.get(task_id, {"deferred": False, "rejected": False, "done": False, "last_priority": None})
        s.update(flags)
        self.task_state[task_id] = s

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

        if any(t.task_id == task_id for t in self.exec_queue):
            return False, "Task already in execution queue."

        used = sum(t.duration for t in self.exec_queue)
        remaining = CAPACITY_DAYS - used
        if task.duration > remaining:
            return False, "Not enough remaining capacity. Use force-insert if needed."

        # schedule
        self.exec_queue.append(task)
        self.treap.delete_by_id(task_id)  # remove from priority repo while scheduled
        self.set_state(task_id, in_exec=True, deferred=False, done=False, last_priority=task.priority)
        return True, "Task inserted into execution queue."

    def force_insert_to_execution_queue(self, task_id: int) -> tuple[bool, str, list]:
        """
        Force-insert a task into the execution queue while respecting 22-day capacity.
        If needed, remove already-scheduled tasks with the lowest priority first to free space.
        Tasks removed from the queue are reinserted into the Treap (priority repo) and marked as not in_exec.
        Returns: (ok, message, removed_tasks_list)
        """
        task = self.get_task(task_id)
        if not task:
            return False, "Task not found.", []

        if any(t.task_id == task_id for t in self.exec_queue):
            return False, "Task already in execution queue.", []

        used = sum(t.duration for t in self.exec_queue)
        remaining = CAPACITY_DAYS - used
        removed = []

        # Need to free space?
        if task.duration > remaining:
            # remove lowest-priority tasks first
            by_lowest = sorted(self.exec_queue, key=lambda x: (x.priority, x.task_id))
            need = task.duration - remaining
            freed = 0
            to_remove_ids = set()

            for cand in by_lowest:
                to_remove_ids.add(cand.task_id)
                freed += cand.duration
                if freed >= need:
                    break

            # rebuild queue without removed
            keep = []
            for t in self.exec_queue:
                if t.task_id in to_remove_ids:
                    removed.append(t)
                else:
                    keep.append(t)
            self.exec_queue = keep

            # tasks we removed go back to Treap and are no longer in_exec
            for r in removed:
                self.treap.insert(r)
                self.set_state(r.task_id, in_exec=False)  # they are not in the monthly queue anymore

            # verify capacity after removals
            remaining = CAPACITY_DAYS - sum(t.duration for t in self.exec_queue)
            if task.duration > remaining:
                # rollback: put queue back as it was and remove reinserts from Treap
                for r in removed:
                    self.treap.delete_by_id(r.task_id)
                self.exec_queue.extend(removed)
                return False, "Not enough capacity even after removing low-priority tasks.", []

        # now there is enough room
        self.exec_queue.append(task)
        self.treap.delete_by_id(task_id)  # remove from Treap while scheduled
        self.set_state(task_id, in_exec=True, deferred=False, done=False, last_priority=task.priority)

        msg = "Task forcibly inserted into execution queue."
        if removed:
            msg += f" Removed {len(removed)} task(s) to free space."
        return True, msg, removed

    def process_waiting(self, approve_all: bool | None = None,
                        approve_ids: set[int] | None = None,
                        reject_ids: set[int] | None = None,
                        bump: int = Added_Priority):
        """
        מאשר/דוחה את הממתינות:
        - approve_all=True  => לאשר את כולן: priority += bump (Hashtable+Treap), לבטל deferred
        - approve_all=False => לדחות את כולן: סימון rejected=True (לא מוחק מה-Hashtable לפי המדיניות שלך)
        - אחרת: לפי approve_ids/reject_ids
        """
        waiting_ids = [tid for tid, st in self.task_state.items()
                       if st.get("deferred") and not st.get("rejected") and not st.get("done")]

        approved, rejected = [], []

        def approve_one(tid: int):
            t = self.table.get_task(tid)
            if not t: return
            new_pr = t.priority + bump
            # עדכון במאגרים:
            self.table.update_task(tid, "priority", new_pr)
            self.treap.update_task_priority(tid, new_pr)  # נשאר ב-Treap (לא בתור), לעדכון לשיבוץ הבא
            self.set_state(tid, deferred=False, rejected=False, last_priority=new_pr)
            approved.append(tid)

        def reject_one(tid: int):
            # לא מוחקים מה-Hashtable לפי המדיניות—רק מסמנים
            self.set_state(tid, deferred=False, rejected=True)
            rejected.append(tid)

        if approve_all is True:
            for tid in waiting_ids: approve_one(tid)
            return approved, rejected

        if approve_all is False:
            for tid in waiting_ids: reject_one(tid)
            return approved, rejected

        approve_ids = approve_ids or set()
        reject_ids = reject_ids or set()

        for tid in waiting_ids:
            if tid in approve_ids:
                approve_one(tid)
            elif tid in reject_ids:
                reject_one(tid)
            # אחרת: משאיר deferred=True למי שלא צוין

        return approved, rejected

    def find_task_full(self, task_id: int) -> dict:
        t = self.table.get_task(task_id)
        in_hash = t is not None
        in_exec = any(x.task_id == task_id for x in self.exec_queue)
        in_treap = self.treap.find_node_by_id(self.treap.root, task_id) is not None

        st = self.task_state.get(task_id, {"in_exec": False, "deferred": False, "rejected": False, "done": False,
                                            "last_priority": None})
        return {
            "task_exists": in_hash or in_exec or in_treap,
            "in_task_repository": in_hash,
            "in_priority_repository": in_treap,
            "in_execution_queue": in_exec,
            "deferred": bool(st["deferred"]),
            "rejected": bool(st["rejected"]),
            "done": bool(st["done"]),
            "priority": (t.priority if t else st["last_priority"]),
            "task": t
        }

    def show_task_status(self, task_id: int) -> str:
        info = self.find_task_full(task_id)
        if not info["task_exists"]:
            return "Task not found in any repository."
        lines = [
            f"Task {task_id} status:",
            f"- In task repository: {'Yes' if info['in_task_repository'] else 'No'}",
            f"- In priority repository: {'Yes' if info['in_priority_repository'] else 'No'}",
            f"- In execution queue (current month): {'Yes' if info['in_execution_queue'] else 'No'}",
            f"- Waiting for approval: {'Yes' if info['deferred'] else 'No'}",
            f"- Rejected: {'Yes' if info['rejected'] else 'No'}",
            f"- Completed in previous months: {'Yes' if info['done'] else 'No'}",
            f"- Current priority: {info['priority'] if info['priority'] is not None else 'Unknown'}",
        ]
        if info["task"]:
            lines.append(f"- Description: {info['task'].description}")
            lines.append(f"- Duration (days): {info['task'].duration}")
        return "\n".join(lines)

    # def schedule(self):
    #     days = [[] for _ in range(22)]
    #     tasks = self.create_priority_queue()
    #     day = 0
    #     for task in tasks:
    #         dur = task.duration
    #         while dur > 0:
    #             days[day].append(task)
    #             dur -= 1
    #             day = (day + 1) % 22
    #     return [f" day {i+1}: {', '.join(str(t) for t in day)}" for i, day in enumerate(days)]

    def print_tasks_by_priority(self):
        return "\n".join(str(t) for t in self.create_priority_queue())

    @property
    def exec_queue_as_list(self):
        return self.exec_queue

    def system_preset(self):
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

        self.init_system()  # איפוס קודם
        for task in tasks:
            self.add_task(task)

        print(f" {len(tasks)} tasks loaded into the system.")

