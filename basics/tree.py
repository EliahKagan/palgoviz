"""Binary trees."""

import collections
import html
import itertools

import graphviz


class Node:
    """A binary tree node."""

    __slots__ = dict(_element=None,
                     left='The left child.',
                     right='The right child.')

    def __init__(self, element, left=None, right=None):
        """Create a binary tree node with the given element and children."""
        self._element = element
        self.left = left
        self.right = right

    def __repr__(self):
        """Representation of the subtree rooted at this node as Python code."""
        return (f'{type(self).__name__}({self.element!r},'
                f' left={self.left!r}, right={self.right!r})')

    @property
    def element(self):
        """The element held in this node."""
        return self._element


def _noop(_):
    """Accept a single argument, but do nothing."""


def _noop_if_none(func):
    """Convert None to a noop function. Otherwise return func unchanged."""
    return _noop if func is None else func


def preorder(root):
    """Recursive preorder (DFS) binary-tree traversal, yielding elements."""
    if root:
        yield root.element
        yield from preorder(root.left)
        yield from preorder(root.right)


def inorder(root):
    """Recursive inorder (DFS) binary-tree traversal, yielding elements."""
    if root:
        yield from inorder(root.left)
        yield root.element
        yield from inorder(root.right)


def postorder(root):
    """Recursive postorder (DFS) binary-tree traversal, yielding elements."""
    if root:
        yield from postorder(root.left)
        yield from postorder(root.right)
        yield root.element


def _do_dfs(root, pre_fn, in_fn, post_fn):
    """Helper for dfs."""
    if not root:
        return

    pre_fn(root.element)
    _do_dfs(root.left, pre_fn, in_fn, post_fn)
    in_fn(root.element)
    _do_dfs(root.right, pre_fn, in_fn, post_fn)
    post_fn(root.element)


def dfs(root, *, pre_fn=None, in_fn=None, post_fn=None):
    """
    Recursive interleaved DFS traversals: preorder, inorder, and postorder.

    Whichever of the preorder, inorder, and postorder functions are passed are
    called at the time a preorder, inorder, or postorder "visitation" occurs.
    Traversal is in a single pass, guaranteeing the relative order of calls.
    """
    return _do_dfs(root,
                   _noop_if_none(pre_fn),
                   _noop_if_none(in_fn),
                   _noop_if_none(post_fn))


def levelorder(root):
    """Level-order (BFS) binary-tree traversal, yielding elements."""
    if not root:
        return

    queue = collections.deque((root,))

    while queue:
        node = queue.popleft()
        yield node.element

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)


def preorder_iterative(root):
    """Nonrecursive preorder binary-tree traversal, yielding elements."""
    if not root:
        return

    stack = [root]

    while stack:
        node = stack.pop()
        yield node.element

        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)


def copy(root):
    """
    Recursively copy a binary tree.

    The new tree's root is returned. The new tree has the same structure, and
    the same objects as elements, but all its nodes are new objects.
    """
    if not root:
        return None

    return Node(root.element, copy(root.left), copy(root.right))


def copy_iterative(root):
    """
    Nonrecursively copy a binary tree.

    This has the same requirements as copy, but it's iterative, not recursive.
    """
    if not root:
        return None

    copied_root = Node(root.element)
    stack = [root, copied_root]

    while stack:
        node, copied_node = stack.pop()

        if node.left:
            copied_node.left = Node(node.left.element)
            stack.append(copied_node.left)

        if node.right:
            copied_node.right = Node(node.right.element)
            stack.append(copied_node.right)

    return copied_root


def height(root):
    """Recursively compute a binary tree's max root-to-leaf path length."""
    return 1 + max(height(root.left), height(root.right)) if root else -1


def height_iterative(root):
    """Nonrecursively compute a binary tree's max root-to-leaf path length."""
    queue = collections.deque()
    if root:
        queue.append(root)

    for height in itertools.count(-1):
        if not queue:
            return height

        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)


def height_iterative_alt(root):
    """
    Nonrecursively compute a binary tree's max root-to-leaf path length.

    This alternative implementation of height_iterative uses a substantially
    different algorithm.
    """
    height = -1
    stack = []
    if root:
        stack.append((root, 0))

    while stack:
        node, depth = stack.pop()

        if not (node.left or node.right):
            height = max(height, depth)
            continue

        if node.left:
            stack.append((node.left, depth + 1))

        if node.right:
            stack.append((node.right, depth + 1))

    return height


def structural_equal(lhs_root, rhs_root):
    """
    Recursively check if two binary trees have the same structure with all
    corresponding elements equal.
    """
    if not (lhs_root and rhs_root):
        return not (lhs_root or rhs_root)

    return (lhs_root.element == rhs_root.element
            and structural_equal(lhs_root.left, rhs_root.left)
            and structural_equal(lhs_root.right, rhs_root.right))


def structural_equal_iterative(lhs_root, rhs_root):
    """
    Nonrecursively check if two binary trees have the same structure with all
    corresponding elements equal.
    """
    stack = [(lhs_root, rhs_root)]

    while stack:
        if not (lhs_root and rhs_root):
            if lhs_root or rhs_root:
                return False
            continue

        if lhs_root.element != rhs_root.element:
            return False

        stack.append((lhs_root.left, rhs_root.left))
        stack.append((lhs_root.right, rhs_root.right))

    return True


def reflect_in_place(root):
    """
    Recursively modify a tree so it becomes its left-right mirror image.

    This uses [FIXME: how much?] auxiliary space.
    """
    if root:
        root.left, root.right = root.right, root.left
        reflect_in_place(root.left)
        reflect_in_place(root.right)


def reflect_in_place_iterative(root):
    """
    Nonrecursively modify a tree so it becomes its left-right mirror image.

    This uses [FIXME: how much?] auxiliary space.
    """
    stack = []
    if root:
        stack.append(root)

    while stack:
        node = stack.pop()
        node.left, node.right = node.right, node.left
        stack.append(node.left)
        stack.append(node.right)


def _check_reflected(left, right):
    """Helper function for is_own_reflection. Compares branches."""
    if not (left and right):
        return not (left or right)

    return (left.element == right.element
            and _check_reflected(left.left, right.right)
            and _check_reflected(left.right, right.left))


def is_own_reflection(root):
    """
    Recursively check if a tree is its own left-to-right mirror image.

    The tree is not modified, even temporarily. It is also not copied.
    """
    return not root or _check_reflected(root.left, root.right)


def is_own_reflection_iterative(root):
    """
    Nonrecursively check if a tree is its own left-to-right mirror image.

    This iterative version of is_own_reflection has the same restrictions.
    """
    if not root:
        return True

    stack = [(root.left, root.right)]

    while stack:
        left, right = stack.pop()

        if not (left and right):
            if left or right:
                return False
            continue

        if left.element != right.element:
            return False

        stack.append((left.left, right.right))
        stack.append((left.right, right.left))

    return True


def draw(root):
    """
    Recursively draw a binary tree.

    This uses the technique due to Eli Bendersky of always drawing point nodes
    for empty branches (that is, where a child attribute is None), so having a
    left but no right child, or a right but no left child, are distinguishable:
    https://eli.thegreenplace.net/2009/11/23/visualizing-binary-trees-with-graphviz

    But the version of the technique used here is modified:

    1. This uses the graphviz module (via https://pypi.org/project/graphviz/)
       for drawing, instead of generating DOT code. (If desired, DOT code can
       then be obtained by calling str on the graphviz.Digraph object.)

    2. Separate nodes whose elements have the same representation, or even
       whose elements are the same object, are supported and drawn separately
       (rather than considered the same node). But the benefits of Bendersky's
       approach are retained: the output is deterministic, depending only on
       the tree's structure and elements. Calling it on a tree twice, or on a
       tree and a copy of the tree, are guaranteed to give the same output,
       including the DOT code (that is, not limited to the visual appearance of
       the drawing), even across separate runs of the program.

    The caller is responsible for ensuring the input really is a binary tree.
    This returns a graphviz.Digraph rather than displaying anything directly.

    This implementation [FIXME: say what kind (or kinds) of traversal is used.]
    """
    graph = graphviz.Digraph()
    counter = itertools.count()

    def draw_subtree(parent):
        parent_name = str(next(counter))

        if parent:
            graph.node(parent_name, label=html.escape(repr(parent.element)))
            graph.edge(parent_name, draw_subtree(parent.left))
            graph.edge(parent_name, draw_subtree(parent.right))
        else:
            graph.node(parent_name, shape='point')

        return parent_name

    draw_subtree(root)
    return graph


def draw_iterative(root):
    """
    Nonrecursively draw a binary tree.

    Like draw, but iterative instead of recursive. This need not have the exact
    behavior of draw. As with draw, separate calls to draw_iterative for
    equivalent trees, even across separate runs of a program, must give the
    same output, including DOT code, as each other. But draw and draw_iterative
    may give different output, so long as their drawings look the same.

    This implementation [FIXME: say what kind (or kinds) of traversal is used.]
    """
    graph = graphviz.Digraph()
    counter = itertools.count()
    stack = [(None, root)]

    while stack:
        parent_name, child = stack.pop()
        child_name = str(next(counter))

        if child:
            graph.node(child_name, label=html.escape(repr(child.element)))
            stack.append((child_name, child.right))
            stack.append((child_name, child.left))
        else:
            graph.node(child_name, shape='point')

        if parent_name is not None:
            graph.edge(parent_name, child_name)

    return graph


def linear_search(root, value):
    """
    Recursive sequential search in a binary tree for an element equal to value.

    Returns a node that holds the matching element, or None if no match.

    If more than one node matches, any may be returned.
    """
    if not root or root.element == value:
        return root

    return linear_search(root.left, value) or linear_search(root.right, value)


def linear_search_iterative(root, value):
    """
    Nonrecursive sequential search in a binary tree for an element equal to
    value.

    This iterative version of linear_search returns a matching node or None.

    If more than one node matches, this is guaranteed to return the same node
    that linear_search would return.
    """
    if not root:
        return None

    stack = [root]

    while stack:
        node = stack.pop()

        if node.element == value:
            return node

        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return None


__all__ = [thing.__name__ for thing in (
    Node,
    preorder,
    inorder,
    postorder,
    dfs,
    levelorder,
    preorder_iterative,
    copy,
    copy_iterative,
    height,
    height_iterative,
    height_iterative_alt,
    structural_equal,
    structural_equal_iterative,
    reflect_in_place,
    reflect_in_place_iterative,
    is_own_reflection,
    is_own_reflection_iterative,
    draw,
    draw_iterative,
    linear_search,
    linear_search_iterative,
)]
