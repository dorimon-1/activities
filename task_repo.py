#Written by:
#תמיד אבני
from task import Task
from linked_list_buckets import LinkedList

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
                idx = self._hash_func(cur.task_id) #מבצעים rehash שזה אומר סידור מחדש של המשימות בדליים בגלל השינוי בגודל הדליים
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

    def __len__(self):
        return sum(len(bucket) for bucket in self.table)

    def all_tasks(self):
        tasks = []
        for bucket in self.table:
            cur = bucket.head
            while cur:
                tasks.append(cur)
                cur = cur.next
        return tasks

    def display(self):
        for i, bucket in enumerate(self.table):
            if len(bucket) > 0:
                print(f"Bucket {i}:")
                bucket.display()


# This script of task manager yet to include functions of integration with 2 data structures.
# TODO: write functions which sends the tasks that were created and inserted to task manager to other data structures.
