#Written by:
#  ישראל-חי זליכה
from task_repo_node import TaskNode

class LinkedList:
    def __init__(self):
        self.head = None

    def _as_node(self, item) -> TaskNode:
        """wrap Task -> TaskNode, pass-through if already TaskNode."""
        if isinstance(item, TaskNode):
            return item
        # כאן item הוא Task
        return TaskNode(item)

    def find(self, task_id):
        cur = self.head
        while cur:
            # cur הוא TaskNode ולכן מזהה דרך cur.task.task_id
            if cur.task.task_id == task_id:
                return cur.task
            cur = cur.next
        return None

    def insert_head(self, item) -> bool:
        """הכנסה לראש (O(1)). מחזיר False אם כפילות.
        מקבל גם Task וגם TaskNode.
        """
        node = self._as_node(item)  # <-- עטיפה אוטומטית אם הגיע Task
        if self.find(node.task.task_id):
            return False
        node.next = self.head
        self.head = node
        return True

    def remove(self, task_id) -> bool:
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
        cur = self.head
        while cur:
            yield cur
            cur = cur.next

    def __len__(self):
        count, cur = 0, self.head
        while cur:
            count += 1
            cur = cur.next
        return count

    def display(self):
        cur = self.head
        while cur:
            print("   ", cur.task)  # <-- הצגה של המשימה מתוך הצומת
            cur = cur.next
