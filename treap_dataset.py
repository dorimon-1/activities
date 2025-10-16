#Written by:
#דור סהר
class TreapNode:
    __slots__ = ("key", "prio", "left", "right", "task")

    def __init__(self, key, prio, task=None):
        self.key = key
        self.prio = prio
        self.left = None
        self.right = None
        self.task = task

def rotate_right(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    return x

def rotate_left(x):
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    return y

def treap_insert(t, key, heap_prio, task):
    if t is None:
        return TreapNode(key, heap_prio, task)
    if key < t.key:
        t.left = treap_insert(t.left, key, heap_prio, task)
        if t.left and t.left.prio > t.prio:
            t = rotate_right(t)
    elif key > t.key:
        t.right = treap_insert(t.right, key, heap_prio, task)
        if t.right and t.right.prio > t.prio:
            t = rotate_left(t)
    else:
        t.prio = heap_prio
        t.task = task
    return t


def treap_search(root, key):
    cur = root
    while cur:
        if key < cur.key:
            cur = cur.left
        elif key > cur.key:
            cur = cur.right
        else:
            return cur
    return None

def treap_merge(left, right):
    if not left or not right:
        return left or right
    if left.prio > right.prio:
        left.right = treap_merge(left.right, right)
        return left
    else:
        right.left = treap_merge(left, right.left)
        return right

def treap_delete(root, key):
    if root is None:
        return None
    if key < root.key:
        root.left = treap_delete(root.left, key)
    elif key > root.key:
        root.right = treap_delete(root.right, key)
    else:
        root = treap_merge(root.left, root.right)
    return root

def treap_collect_all(root, acc):
    if not root:
        return
    acc.append(root)
    treap_collect_all(root.left, acc)
    treap_collect_all(root.right, acc)

def treap_inorder(root, acc):
    if not root:
        return
    treap_inorder(root.left, acc)
    acc.append(root)
    treap_inorder(root.right, acc)

class Treap:
    def __init__(self):
        self.root = None

    def insert(self, task):
        key = (task.priority, task.task_id)
        heap_prio = task.priority # heap priority -> MAX-HEAP
        self.root = treap_insert(self.root, key, heap_prio, task)
        return True

    def peek_max(self):
        return self.root.task if self.root and self.root.task else None

    def pop_max(self):
        if not self.root:
            return None
        max_task = self.root.task
        self.root = treap_merge(self.root.left, self.root.right)
        return max_task

    def find_node_by_id(self, node, task_id):
        if not node:
            return None
        if node.task and node.task.task_id == task_id:
            return node
        left = self.find_node_by_id(node.left, task_id)
        if left: return left
        return self.find_node_by_id(node.right, task_id)

    def delete_by_id(self, task_id):
        node = self.find_node_by_id(self.root, task_id)
        if not node:
            return False
        self.root = treap_delete(self.root, node.key)
        return True

    def update_task_priority(self, task_id, new_priority):
        node = self.find_node_by_id(self.root, task_id)
        if not node or not node.task:
            return False
        self.root = treap_delete(self.root, node.key)
        node.task.priority = new_priority
        return self.insert(node.task)

    def to_list(self, order="des"):
        nodes = []
        treap_inorder(self.root, nodes)
        tasks = [n.task for n in nodes if n.task]
        if order == "desc":
            tasks.reverse()
        return tasks

    def clear(self):
        self.root = None

    def __len__(self):
        nodes = []
        treap_collect_all(self.root, nodes)
        return len([n for n in nodes if n.task])
