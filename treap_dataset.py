class TreapNode:
    __slots__ = ("key", "prio", "left", "right", "task")
    def __init__(self, key, prio, task = None):
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

def treap_insert(t, key, value):
    if t is None:
        t = TreapNode(key, value)
        return t
    if key < t.key:
        t.left = treap_insert(t.left, key, value)
        if t.left and t.left.prio > t.prio:
            t = rotate_right(t)
    elif key > t.key:
        t.right = treap_insert(t.right, key, value)
        if t.right and t.right.prio > t.prio:
            t = rotate_left(t)
    else:
        t.prio = value
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
