class LinkedList:
    def __init__(self):
        self.head = None

    def find(self, task_id):
        cur = self.head
        while cur:
            if cur.task_id == task_id:
                return cur
            cur = cur.next
        return None

    def insert_head(self, task: Task) -> bool:
        """הכנסה לראש (O(1)). מחזיר False אם כפילות."""
        if self.find(task.task_id):
            return False
        task.next = self.head
        self.head = task
        return True

    def remove(self, task_id) -> bool:
        prev, cur = None, self.head
        while cur:
            if cur.task_id == task_id:
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
            print("   ", cur)
            cur = cur.next