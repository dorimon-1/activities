#Written by:
#דור סהר
class TreapNode:
    """
    Node for Treap structure.

    Attributes:
        key: Key for BST ordering (tuple: priority, task_id).
        prio: Heap priority (used for heap property in Treap).
        left: Left child node.
        right: Right child node.
        task: Associated Task object.
    """
    __slots__ = ("key", "prio", "left", "right", "task")

    def __init__(self, key, prio, task=None):
        self.key = key
        self.prio = prio
        self.left = None
        self.right = None
        self.task = task


def rotate_right(y):
    """
    Performs a right rotation on a subtree rooted at y.

    Returns:
        TreapNode: new root after rotation.
    """
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    return x


def rotate_left(x):
    """
    Performs a left rotation on a subtree rooted at x.

    Returns:
        TreapNode: new root after rotation.
    """
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    return y


def treap_insert(t, key, heap_prio, task):
    """
    Inserts a task into the Treap while maintaining BST and heap properties.

    Returns:
        TreapNode: new root after insertion.
    """
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
    """Searches for a node by key in the Treap."""
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
    """Merges two treaps and returns the new root."""
    if not left or not right:
        return left or right
    if left.prio > right.prio:
        left.right = treap_merge(left.right, right)
        return left
    else:
        right.left = treap_merge(left, right.left)
        return right


def treap_delete(root, key):
    """Deletes a node by key from the Treap."""
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
    """Collects all nodes in the Treap into a list."""
    if not root:
        return
    acc.append(root)
    treap_collect_all(root.left, acc)
    treap_collect_all(root.right, acc)


def treap_inorder(root, acc):
    """In-order traversal of the Treap, storing nodes in acc."""
    if not root:
        return
    treap_inorder(root.left, acc)
    acc.append(root)
    treap_inorder(root.right, acc)


class Treap:
    """Treap structure combining BST ordering by key and heap by priority."""

    def __init__(self):
        self.root = None

    def insert(self, task):
        """Inserts a task into the Treap based on (priority, task_id)."""
        key = (task.priority, task.task_id)
        heap_prio = task.priority
        self.root = treap_insert(self.root, key, heap_prio, task)
        return True

    def peek_max(self):
        """Returns the task with maximum priority without removing it."""
        return self.root.task if self.root and self.root.task else None

    def pop_max(self):
        """Removes and returns the task with maximum priority."""
        if not self.root:
            return None
        max_task = self.root.task
        self.root = treap_merge(self.root.left, self.root.right)
        return max_task

    def find_node_by_id(self, node, task_id):
        """Finds a TreapNode by its task_id."""
        if not node:
            return None
        if node.task and node.task.task_id == task_id:
            return node
        left = self.find_node_by_id(node.left, task_id)
        if left: return left
        return self.find_node_by_id(node.right, task_id)

    def delete_by_id(self, task_id):
        """Deletes a task from the Treap by task_id."""
        node = self.find_node_by_id(self.root, task_id)
        if not node:
            return False
        self.root = treap_delete(self.root, node.key)
        return True

    def update_task_priority(self, task_id, new_priority):
        """Updates the priority of a task in the Treap."""
        node = self.find_node_by_id(self.root, task_id)
        if not node or not node.task:
            return False
        self.root = treap_delete(self.root, node.key)
        node.task.priority = new_priority
        return self.insert(node.task)

    def to_list(self, order="des"):
        """Returns a list of tasks in-order (ascending or descending by priority)."""
        nodes = []
        treap_inorder(self.root, nodes)
        tasks = [n.task for n in nodes if n.task]
        if order == "desc":
            tasks.reverse()
        return tasks

    def clear(self):
        """Clears the Treap."""
        self.root = None

    def __len__(self):
        """Returns the number of tasks in the Treap."""
        nodes = []
        treap_collect_all(self.root, nodes)
        return len([n for n in nodes if n.task])
