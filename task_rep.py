from task import Task
from task_rep_node import TaskNode
from linked_list_buckets import LinkedList
from task_status import Status


class Hashtable:
    def __init__(self, capacity=50):
        self.capacity = max(1, capacity)
        # כל דלי הוא רשימה מקושרת (שרשור)
        self.table = [LinkedList() for _ in range(self.capacity)]

    def _hash_func(self, task_id):
        return task_id % self.capacity

    def _rehash(self):
        old_table = self.table
        self.capacity *= 2  # מגדילים פי 2
        self.table = [LinkedList() for _ in range(self.capacity)]

        for bucket in old_table:
            cur = bucket.head
            while cur:
                next_node = cur.next  # לשמור לפני שננתק
                cur.next = None  # מנתקים מהשרשרת הישנה
                idx = self._hash_func(cur.task_id)
                self.table[idx].insert_head(cur)
                cur = next_node

    def add_task(self, task: Task) -> bool:

        # אם עומס גבוה מדי → ריהאש
        if len(self) / self.capacity > 2:
            self._rehash()

        idx = self._hash_func(task.task_id)
        # הכנסה לראש הדלי (O(1)) למעט בדיקת כפילות O(n_bucket)
        return self.table[idx].insert_head(task)

    def get_task(self, task_id):
        idx = self._hash_func(task_id)
        return self.table[idx].find(task_id)

    def remove_task(self, task_id) -> bool:
        idx = self._hash_func(task_id)
        return self.table[idx].remove(task_id)

    def update_task(self, task_id, field: str, new_value) -> bool:
        t: Task = self.get_task(task_id)

        if not t:
            return False

        if field == "description":
            t.set_description(str(new_value))
        elif field == "priority":
            t.set_priority(int(new_value))
        elif field == "duration":
            t.set_duration(int(new_value))
        elif field == "status":

            match new_value:
                case 1:
                    t.mark_pending()

                case 2:
                    t.mark_scheduled()

                case 3:
                    t.mark_completed()

                case 4:
                    t.mark_cancelled()

                case 5:
                    t.mark_delayed()

                case 6:
                    t.mark_in_progress()

                case _:
                    return False
        else:
            return False

        return True

    def __len__(self):
        return sum(len(bucket) for bucket in self.table)

    def display(self):
        for i, bucket in enumerate(self.table):
            if len(bucket) > 0:
                print(f"Bucket {i}:")
                bucket.display()

# This script of task manager yet to include functions of integration with 2 data structures.
# TODO: write functions which sends the tasks that were created and inserted to task manager to other data structures.
