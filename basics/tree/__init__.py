"""
Binary trees.

In most binary trees, including those used in this module, empty branches are
represented as "null" sentinels. In Python this is the special None object.
There are two conventions for how we describe these trees, which affect the
answers to questions like, "How many nodes are in the tree?"

The most common convention, which we use, is that these branches are truly
empty. So None represents the absence of a node. It does not represent a leaf.
A node whose children are both given as None is a leaf.

The other convention is to regard the sentinels as the actual leaves, as in The
Art of Computer Programming by Donald Knuth. We don't use this convention. But:

1. Unless otherwise documented, functions that accept a tree by taking its root
   node as an argument also accept an empty "tree" when None is passed. Really,
   there is no such thing as an empty tree, and what we call an empty tree is a
   forest of zero trees. But broadening what we regard to be a tree in this way
   is common, very useful, and often makes implementations more elegant.

2. When we draw the trees with Graphviz--which the draw, draw_iterative, and
   draw_extended functions do--we draw point nodes for empty branches. See the
   docstrings for details. That is, we draw the trees as conceptualized by
   Knuth, even though we do not otherwise regard None to represent a node. We
   do this to ensure that left and right children are always distinguished.

Some of our functions create or add nodes to trees. Except as otherwise stated:

1. Functions that create new tree nodes create Node instances and, if
   applicable, may assume input trees' nodes are of that type.

2. Other functions work equally well on trees made of Node, FrozenNode, or any
   object that has element, left, and right attributes with the same meanings.

Finally, two general design notes:

1. Infinite trees are meaningful and can even be represented using lazy
   techniques. But classes and functions in this module assume finite trees.

2. A tree can be so tall that RecursionError would be raised when attempting to
   traverse it with a recursive algorithm. Unless stated otherwise, it is okay
   for recursive functions in this module to be limited in this way (even when
   their descriptions do not insist they be implemented recursively).
"""

import collections
import contextlib
import html
import itertools
import math
import types

import graphviz

from . import examples, green


class _NodeReprMixin:
    """Base class to supply nice repr functionality for binary tree nodes."""

    __slots__ = ()

    def __repr__(self):
        """Recursive representation of this node as Python code."""
        if not (self.left or self.right):  # This is a leaf.
            return f'{type(self).__name__}({self.element!r})'

        return (f'{type(self).__name__}({self.element!r},'
                f' {self.left!r}, {self.right!r})')


class Node(_NodeReprMixin):
    """A binary tree node."""

    __slots__ = dict(_element=None,
                     left='The left child.',
                     right='The right child.')

    def __init__(self, element, left=None, right=None):
        """Create a binary tree node with the given element and children."""
        self._element = element
        self.left = left
        self.right = right

    @property
    def element(self):
        """The element held in this node."""
        return self._element


class FrozenNode(_NodeReprMixin):
    """
    A binary tree node without mutable state.

    Node and FrozenNode are both immutable, in that both use reference-based
    equality comparison, whose result does not change even when attributes do.
    But Node facilitates changing its child references; FrozenNode does not.

    Node thus builds mutable trees, while FrozenNode builds immutable trees,
    relative to structural equality comparison of trees; see structural_equal
    below. This module does not encapsulate whole trees as class instances,
    which is often useful, especially for BSTs; see build_bst below. Nor does
    it treat nodes as the trees they root (one would define their operations as
    methods instead of top-level functions, structural_equal becoming __eq__),
    as there are design subtleties for base cases; see calc.Atom/calc.Compound.
    So this mutability/immutability isn't relative to any actual == comparison.
    """

    __slots__ = ('_element', '_left', '_right')

    def __init__(self, element, left=None, right=None):
        """Create a binary tree node with the given element and children."""
        self._element = element
        self._left = left
        self._right = right

    @property
    def element(self):
        """The element held in this node."""
        return self._element

    @property
    def left(self):
        """The left child."""
        return self._left

    @property
    def right(self):
        """The right child."""
        return self._right


def _noop(_):
    """Accept a single argument, but do nothing."""


def _noop_fallback(func):
    """Convert None to a noop function. Otherwise return func unchanged."""
    return _noop if func is None else func


def preorder(root):
    """
    Recursive preorder (DFS) binary-tree traversal, yielding elements.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if root:
        yield root.element
        yield from preorder(root.left)
        yield from preorder(root.right)


def inorder(root):
    """
    Recursive inorder (DFS) binary-tree traversal, yielding elements.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if root:
        yield from inorder(root.left)
        yield root.element
        yield from inorder(root.right)


def postorder(root):
    """
    Recursive postorder (DFS) binary-tree traversal, yielding elements.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if root:
        yield from postorder(root.left)
        yield from postorder(root.right)
        yield root.element


def _do_general_dfs(root, pre_fn, in_fn, post_fn):
    """Helper for general_dfs."""
    if not root:
        return

    pre_fn(root.element)
    _do_general_dfs(root.left, pre_fn, in_fn, post_fn)
    in_fn(root.element)
    _do_general_dfs(root.right, pre_fn, in_fn, post_fn)
    post_fn(root.element)


def general_dfs(root, *, pre_fn=None, in_fn=None, post_fn=None):
    """
    Recursive interleaved DFS traversals: preorder, inorder, and postorder.

    Whichever of the pre_fn, in_fn, and post_fn functions are passed are called
    on preorder, inorder, and postorder visitation, respectively. Traversal is
    in a single pass, guaranteeing the relative order of calls.

    Consider this form of DFS on binary trees that traverses but does nothing:

        def skeletal_dfs(root):
            if root:
                skeletal_dfs(root.left)
                skeletal_dfs(root.right)

    All forms of recursively implemented DFS on a binary tree are based on that
    logic. (They may be in a different style, may use results of subcalls, and
    may be generator or asynchronous functions instead of regular functions.)

    Examining what preorder, inorder, and postorder traversals each add to that
    skeleton shows that a generalized binary-tree DFS is possible, by adding
    code corresponding to what all three add. This performs any combination of
    preorder, inorder, and postorder actions. If none of pre_fn, in_fn, and
    post_fn are passed, this works like skeletal_dfs. If only one is passed,
    it behaves like preorder, inorder, or postorder. With more than one, this
    combines and interleaves the effects of any two, or all three, of preorder,
    inorder, and postorder, without having to traverse the tree more than once.

    It is occasionally useful to call this generalized function. But the main
    point of this is to show that preorder, inorder, and postorder actions can
    be used together. Many highly specialized traversals do so. Furthermore,
    many recursive algorithms that are not obviously related to trees can be
    understood, through this lens, as traversal in implicit tree structures.
    Divide and conquer algorithms divide the work (preorder), make recursive
    calls, and combine the results (postorder). Some of them do some of their
    dividing or combining or other work in between recursive calls (inorder).

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    return _do_general_dfs(root,
                           _noop_fallback(pre_fn),
                           _noop_fallback(in_fn),
                           _noop_fallback(post_fn))


# FIXME: Having completed dfs above, consider mergesort. It is a divide and
# conquer algorithm in which each recursive case (internal node) has two
# children. The children are even identifiable as left and right. Add a brief
# explanation to the recursion.merge_sort docstring about what combination of
# preorder, inorder, and postorder actions it has. If it has only one kind, say
# how mergesort facilitates that, and whether this is true of all forms of
# recursive mergeort (if implemented reasonably). Otherwise, include a brief
# description of another form of mergesort that would only have one kind.


def levelorder(root):
    """
    Level-order (BFS) binary-tree traversal, yielding elements.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
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
    """
    Nonrecursive preorder binary-tree traversal, yielding elements.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
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


def size(root):
    """
    Compute the number of nodes in a binary tree.

    This implementation is very simple because it uses an existing function in
    this module (that is not about size).

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    return sum(1 for _ in preorder(root))


def size_recursive(root):
    """
    Recursively compute the number of nodes in a binary tree.

    This implementation is recursive, not using other functions in this module.
    """
    if not root:
        return 0

    return 1 + size_recursive(root.left) + size_recursive(root.right)


def size_iterative(root):
    """
    Nonrecursively compute the number of nodes in a binary tree.

    This implementation is iterative, not using other functions in this module.
    """
    count = 0
    stack = []

    if root:
        stack.append(root)

    while stack:
        count += 1
        node = stack.pop()
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)

    return count


def height(root):
    """
    Recursively compute a binary tree's maximum root-to-leaf path length.

    We define the height of an empty "tree" (that is, when root is None) as -1.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    return 1 + max(height(root.left), height(root.right)) if root else -1


def height_iterative(root):
    """
    Nonrecursively compute a binary tree's maximum root-to-leaf path length.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
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
    Nonrecursively compute a binary tree's maximum root-to-leaf path length.

    This alternative implementation of height_iterative uses a substantially
    different algorithm.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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


def copy(root):
    """
    Recursively copy a binary tree.

    The new tree's root is returned. The new tree has the same structure, and
    the same objects as elements, but all its nodes are new Node objects.

    [FIXME: State the time complexity, for a tree of n nodes and height h.]
    """
    if not root:
        return None

    return Node(root.element, copy(root.left), copy(root.right))


def copy_iterative(root):
    """
    Nonrecursively copy a binary tree.

    This has the same requirements as copy, but it's iterative, not recursive.

    [FIXME: State the time complexity, for a tree of n nodes and height h.]
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


def structural_equal(lhs_root, rhs_root):
    """
    Recursively check if two binary trees have the same structure with all
    corresponding elements equal.

    Only structure and element values are considered, not node type. Trees of
    Node and trees of FrozenNode can thus be structurally equal to each other.
    (In this way, this is more like set equality than sequence equality.)

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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

    This is the iterative version of structural_equal.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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
    Recursively modify a tree into its left-right mirror image.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if root:
        root.left, root.right = root.right, root.left
        reflect_in_place(root.left)
        reflect_in_place(root.right)


def reflect_in_place_iterative(root):
    """
    Nonrecursively modify a tree into its left-right mirror image.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    return not root or _check_reflected(root.left, root.right)


def is_own_reflection_iterative(root):
    """
    Nonrecursively check if a tree is its own left-to-right mirror image.

    This iterative version of is_own_reflection has the same restrictions.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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

    1. This uses the graphviz module (https://pypi.org/project/graphviz/) for
       drawing, instead of generating DOT code. (If desired, DOT code can then
       be obtained by calling str on the graphviz.Digraph object.)

    2. Separate nodes whose elements have the same representation, or even
       whose elements are the same object, are supported and drawn separately
       (rather than considered the same node). But the benefits of Bendersky's
       approach are retained: the output is deterministic, depending only on
       the tree's structure and elements. Calling it on a tree twice, or on a
       tree and a copy of the tree, are guaranteed to give the same output,
       including the DOT code (that is, not limited to the visual appearance of
       the drawing), even across separate runs of the program.

    If the same node object appears in multiple places, this still draws
    separate subtrees. Other than such duplication, the caller must ensure the
    input is a binary tree. A graphviz.Digraph is returned rather than
    displaying anything directly. No caching is performed across calls to draw.

    This implementation [FIXME: say what kind (or kinds) of traversal is used.]
    """
    graph = graphviz.Digraph()
    names = map(str, itertools.count())

    def draw_subtree(parent):
        parent_name = next(names)

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
    may give different output, so long as their drawings look the same. Other
    requirements are the same.

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

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
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


def linear_search_mindepth(root, value):
    """
    Sequential search in a binary tree for a shallowest element equal to value.

    This is like linear_search/linear_search_iterative, but of all nodes that
    contain an element equal to value, one of them of minimal distance from the
    root is returned. If there are multiple such minimum-depth nodes, any may
    be returned. If no node's element is equal to value, None is returned.

    The algorithm works well on most or all inputs, but it is optimized to run
    fast when each node's probability of holding an element equal to value is
    greater than 1/n (with n total nodes).

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if not root:
        return None

    queue = collections.deque((root,))

    while queue:
        node = queue.popleft()

        if node.element == value:
            return node

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return None


def linear_search_mindepth_alt(root, value):
    """
    Sequential search in a binary tree for a shallowest element equal to value.

    This is like linear_search_mindepth but it uses a very different algorithm.
    One of them is recursive and the other iterative. Their worst-case
    asymptotic time complexities are the same. But while linear_search_mindepth
    is time optimized for when each node's probability of holding an element
    equal to value is greater than 1/n, this is instead auxiliary-space
    optimized for when that probability is less than 1/n.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    def dfs(node, depth):
        if not node:
            return math.inf, None
        if node.element == value:
            return depth, node

        left_depth, left = dfs(node.left, depth + 1)
        right_depth, right = dfs(node.right, depth + 1)

        if right_depth < left_depth:
            return right_depth, right
        return left_depth, left

    _, result = dfs(root, 0)
    return result


def _get_path(root, value):
    """Return a list of nodes in a path from the root to a node with value."""
    path = []

    def dfs(node):
        if not node:
            return None
        path.append(node)
        if node.element == value:
            return path
        return dfs(node.left) or dfs(node.right)

    result = dfs(root)
    if not result:
        raise ValueError(f'no node with value {value!r} found')
    return result


def nearest_ancestor(root, value1, value2):
    """
    Find the lowest common ancestor of nodes with elements value1 and value2.

    It is guaranteed that the tree rooted at root has exactly one node holding
    value1 and exactly one node holding value2. Given this restriction, there
    is always exactly one nearest ancestor node. It may be the root. If value1
    and value2 are equal, then they are in the same node, which we consider to
    be its own ancestor (and thus the nearest ancestor in common with itself).

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    path1 = _get_path(root, value1)
    path2 = _get_path(root, value2)
    zipped_reversed = zip(reversed(path1), reversed(path2))
    return next(node1 for node1, node2 in zipped_reversed if node1 is node2)


def is_bst(root):
    """
    Recursively check if a binary tree is a binary search tree (BST).

    This implementation is based on how a BST can be defined as [FIXME: what?].

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.
    The time complexity should be asymptotically optimal for this problem. Say
    why it is not possible for any asymptotically faster solution to exist.]
    """
    return not any(cur < pre for pre, cur in itertools.pairwise(inorder(root)))


def is_bst_alt(root):
    """
    Recursively check if a binary tree is a binary search tree (BST).

    One of is_bst and is_bst_alt is self-contained except for its own helpers,
    if any. The other uses an existing recursive function in this module (that
    is not about BSTs) to do some of its work, and is not otherwise recursive.

    This implementation is based on how a BST can be defined as [FIXME: what?].
    The definition in is_bst, and this, are equivalent, even though they sound
    quite different (with code one writes to express them likewise differing).

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.
    Time complexity is as in is_bst. If auxiliary space differs, explain.]
    """
    unbounded = object()

    def is_bounded_bst(node, lower, upper):
        if not node:
            return True

        return ((lower is unbounded or not node.element < lower) and
                (upper is unbounded or not upper < node.element) and
                is_bounded_bst(node.left, lower, node.element) and
                is_bounded_bst(node.right, node.element, upper))

    return is_bounded_bst(root, unbounded, unbounded)


def is_bst_iterative(root):
    """
    Nonrecursively check if a binary tree is a binary search tree (BST).

    This iterative implementation is conceptually similar to one of is_bst or
    is_bst_alt. Recursion is not used, not even indirectly.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.
    Time complexity is as in is_bst. If auxiliary space differs, explain.]
    """
    if not root:
        return True

    unbounded = object()
    stack = [(root, unbounded, unbounded)]

    while stack:
        node, lower, upper = stack.pop()

        if lower is not unbounded and node.element < lower:
            return False
        if upper is not unbounded and upper < node.element:
            return False

        if node.left:
            stack.append((node.left, lower, node.element))
        if node.right:
            stack.append((node.right, node.element, upper))

    return True


def binary_search(root, value):
    """
    Recursive binary search in a binary search tree (BST).

    The caller is responsible for ensuring the tree is a BST, with at least a
    weak ordering among the tree's elements and the value argument. A node
    whose element is similar to (neither less nor greater than) value is
    returned, unless there is no such node, in which case None is returned.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if not root:
        return None
    if value < root.element:
        return binary_search(root.left, value)
    if value > root.element:
        return binary_search(root.right, value)
    return root


def binary_search_iterative(root, value):
    """
    Nonrecursive binary search in a binary search tree (BST).

    Like binary_search, this returns a node whose element is similar to value,
    or None if there is no such node.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    while root:
        if value < root.element:
            root = root.left
        elif value > root.element:
            root = root.right
        else:
            return root

    return None


def binary_insert(root, element, *, allow_duplicate=False):
    """
    Recursively insert a new node in a BST, keeping it a BST.

    The allow_duplicate parameter specifies whether a new node should be added
    even if one or more existing nodes' elements are similar to element.

    The tree is never spliced or rebalanced: all preexisting paths from a root
    to any node continue to be paths in the tree after a new node is added.

    The updated tree's root node is returned, though this will be the same as
    the old root node unless the tree was empty and there was no such node.

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    def insert(node):
        if not node:
            return Node(element)

        if element < node.element:
            node.left = insert(node.left)
        elif allow_duplicate or element > node.element:
            node.right = insert(node.right)

        return node

    return insert(root)


def binary_insert_iterative(root, element, *, allow_duplicate=False):
    """
    Nonrecursively insert a new node in a BST, keeping it a BST.

    See binary_insert. This is the iterative version. It has the same effect on
    the tree as binary_insert, including when multiple distinct modifications
    to the tree could be correct, which happens [FIXME: finish this sentence].

    [FIXME: State time and auxiliary space for a tree of n nodes and height h.]
    """
    if not root:
        return Node(element)

    node = root

    while True:
        if element < node.element:
            if not node.left:
                node.left = Node(element)
                break
            node = node.left
        elif allow_duplicate or element > node.element:
            if not node.right:
                node.right = Node(element)
                break
            node = node.right
        else:
            break

    return root


def build_bst(iterable, *, multiset=False):
    """
    Build a binary search tree from the given elements.

    This uses an existing function. It makes no element comparisons directly.

    The multiset parameter specifies if multiple elements that compare similar
    (neither greater nor less than each other) are all inserted, or just one.

    TODO: In many applications, it is not necessary to hand out references to
    individual nodes. Then it's best to encapsulate the logic of building and
    operating on a BST in a class: in Python, usually a Set (often MutableSet)
    or Mapping (often MutableMapping) class. When this project gains such a
    class, it should support inserting elements, but also deleting elements.

    [FIXME: State best, average, and worst-case time, for a length-n iterable.]
    """
    root = None
    for element in iterable:
        binary_insert(root, element, allow_duplicate=multiset)
    return root


def tree_sort(iterable):
    """
    Sort values, by [FIXME: briefly say how].

    This BST-based technique returns an iterable of sorted values. It has
    [FIXME: State best, average, and worst-case time and space complexities,
    for a length-n input iterable.]
    """
    return inorder(build_bst(iterable, multiset=True))


def _do_find_subtree(tree, nonempty_subtree):  # TODO: Should this be a helper?
    """Recursive helper for find_subtree."""
    if not tree:
        return None

    if structural_equal(tree, nonempty_subtree):
        return tree

    return (_do_find_subtree(tree.left, nonempty_subtree) or
            _do_find_subtree(tree.right, nonempty_subtree))


def find_subtree(tree, subtree):
    """
    Find a copy of a subtree in a binary tree, if present, in quadratic time.

    This looks for a subtree of tree with the same structure as, and all
    corresponding elements equal to, the subtree argument. If such a subtree
    exists, its root is returned; otherwise None is returned. The elements may
    be any objects (assuming equality comparison is not broken). In particular,
    tree and subtree need not be binary search trees, and they probably aren't.

    The tree argument is the root node of the corpus--the tree being searched
    in. The subtree argument is the root node of the pattern--the tree being
    searched for. It's possible that subtree is actually a node in tree, in
    which case there is a match. But usually when there is a match, subtree is
    still not a node in tree, but instead is the root of a tree structurally
    equal to some actual subtree of tree. Thus "corpus" and "pattern" (or
    "haystack" and "needle") would be more accurate (but less intuitive) names.

    The tree and/or subtree arguments may be None. As in other functions in
    this module, None indicates an empty "tree". Because we treat empty "trees"
    as trees, an empty pattern is always a match. If the corpus is also empty,
    they are the same "tree". Otherwise, because the corpus is finite, it has a
    leaf, which has two empty branches; an empty pattern matches an empty
    branch. None is thus returned if there is no match or if subtree is None.

    This is the naive algorithm. If tree has m nodes and subtree has n nodes,
    with m > 0 and n > 0, this takes O(m * n) time and uses [FIXME: how much?]
    auxiliary space.
    """
    return _do_find_subtree(tree, subtree) if subtree else None


def _memoize_subtrees(root, memo, factory):
    """
    Find or record a subtree that matches root in the memo table. Return it.

    By left-to-right postorder traversal, each subtree of the tree rooted at
    root, if isn't structurally equal to (that is, if it doesn't match) any
    tree recorded in memo, is recorded in memo.

    memo is expected to be a mapping, empty except entries added by prior calls
    to _memoize_subtrees. If no tree matching the tree rooted at root was seen
    before, then memo must be mutable, or TypeError is raised. There is no
    guarantee on how data are represented in memo.

    If factory is None, existing nodes are memoized and returned. In that case,
    the caller must ensure that, if a subtree rooted at a memoized node is
    mutated, no subsequent call is made with that memo table (unless cleared).
    If factory is not None, it is expected to a binary tree node type, and it
    is used to construct the nodes that are memoized and returned. Calls that
    reuse the same memo argument should use the same factory argument, too.
    """
    if not root:
        return None

    key = (root.element,
           _memoize_subtrees(root.left, memo, factory),
           _memoize_subtrees(root.right, memo, factory))

    try:
        return memo[key]
    except KeyError:
        result = memo[key] = (root if factory is None else factory(*key))
        return result


def find_subtree_fast(tree, subtree):
    """
    Find a copy of a subtree in a binary tree, if present, in linear time.

    This is like find_subtree, but it uses a more clever algorithm. But this
    only works if all the elements are hashable. Nothing else is known about
    the elements; as in find_subtree, tree and subtree need not be BSTs. If
    tree has m nodes and subtree has n nodes, this takes O(m + n) time and uses
    [FIXME: how much?] auxiliary space.
    """
    if not (tree and subtree):
        return None

    memo = {}
    _memoize_subtrees(tree, memo, None)

    try:
        return _memoize_subtrees(subtree, types.MappingProxyType(memo), None)
    except TypeError:
        return None


def copy_compact(root):
    """
    Copy a binary tree as a FrozenNode tree with all subtrees de-duplicated.

    This only supports input trees whose elements are all hashable objects.

    Reusing subtrees is often a good idea for immutable trees, like the tree
    this builds. It is far less often appropriate for mutable trees, so copy
    and copy_iterative do not do so. This is because [FIXME: explain].

    For simplicity, the returned tree's nodes are all newly created. None are
    shared with the input tree, even if the input tree is a FrozenNode tree.
    This never creates any nodes besides those that appear in the output tree.

    The time complexity is asymptotically optimal. [FIXME: State the time
    complexity for n nodes and height h.]
    """
    return _memoize_subtrees(root, {}, FrozenNode)


# FIXME: Having implemented find_subtree_fast and copy_compact, make any
# changes needed so they share much (perhaps most) of their logic. Factor their
# shared logic into a shared helper function. It must have a descriptive name,
# as well as a docstring explaining what it does, which may need more than just
# its initial summary line. Make sure you do this in a way you are confident is
# a reasonable and non-contrived approach to implementing find_subtree_fast and
# copy_compact, and that demonstrates the conceptual connection between them
# (even without reading docstrings or comments). They must not call each other,
# only the helper. Calling find_subtree_fast must never create any tree nodes.
#
# If find_subtree_fast previously had two helper functions with similar logic
# (even if their code was mostly different), that will no longer be the case.
# It is unlikely either find_subtree_fast or compact_compact will have helpers
# besides the one they will now share. Furthermore, at least one of them must
# not only use no other helpers, but also, its body must consist of a single
# return statement that is clear and fits easily on one line.
#
# This can all be done before or after implementing draw_extended below. If,
# after doing this and committing the result, you decide you prefer not to
# share the logic this way, feel free to make further changes, so long as you
# regard your ultimate implementations to be as or more elegant than this way.


_COLORS_SOLID = dict(color='black', fontcolor='black')
"""Color options for Graphviz to show a node as solid (not faded)."""


_COLORS_FADED = dict(color='lightgray', fontcolor='lightgray')
"""Color options for Graphviz to show a node as faded."""


def _draw_extended_faded(root):
    """Helper for draw_extended, covering dag=False."""
    graph = graphviz.Digraph()
    names = map(str, itertools.count())
    vis = set()

    def draw_subtree(parent, colors):
        parent_name = next(names)

        if not parent:
            graph.node(parent_name, shape='point', **colors)
            return parent_name

        if parent in vis:
            colors = _COLORS_FADED
        else:
            vis.add(parent)

        parent_label = html.escape(repr(parent.element))
        graph.node(parent_name, label=parent_label, **colors)
        graph.edge(parent_name, draw_subtree(parent.left, colors), **colors)
        graph.edge(parent_name, draw_subtree(parent.right, colors), **colors)
        return parent_name

    draw_subtree(root, _COLORS_SOLID)
    return graph


def _draw_extended_dag(root):
    """Helper for draw_extended, covering dag=True."""
    graph = graphviz.Digraph()
    names = map(str, itertools.count())
    memo = {}

    def draw_subtree(parent):
        with contextlib.suppress(KeyError):
            return memo[parent]

        parent_name = next(names)

        if not parent:
            graph.node(parent_name, shape='point')
            return parent_name

        memo[parent] = parent_name
        graph.node(parent_name, label=html.escape(repr(parent.element)))
        left_name = draw_subtree(parent.left)
        graph.edge(parent_name, left_name, label='L', fontcolor='gray')
        right_name = draw_subtree(parent.right)
        graph.edge(parent_name, right_name, label='R', fontcolor='gray')

        return parent_name

    draw_subtree(root)
    return graph


def draw_extended(root, dag=False):
    """
    Draw a binary tree, identifying de-duplicated subtrees.

    If dag=False, then for each subtree reused in multiple places (as in output
    of copy_compact), all but one occurrence is drawn with all nodes and edges
    faded out. That is, others are drawn in some light shade of gray instead of
    black. As in draw and draw_iterative, edges are not labeled.

    If dag=True, the directed acyclic graph structure of the nodes in memory is
    drawn: even reused nodes are drawn just once, and the drawing is of a DAG
    whose maximum outdegree is 2. If no nodes are reused, this DAG is a binary
    tree; otherwise, it is not a tree at all (because a rooted tree has exactly
    one path from the root to any node). Empty branches are still drawn
    separately, so multiple edges will never come into the same point "node."
    Shared branches may end up crossed: an edge from a node to its left child
    may appear to the right of an edge from the same node to its right child.
    To compensate, each edge is labeled with an "L" or an "R". These labels are
    always colored some suitable shade of gray, but nothing else is ever faded.

    (See object_graph.draw_tuple and class_graph.draw, which also draw DAGs.)

    Separate draw_extended calls with the same dag argument, on the same tree
    or on different trees whose representations in memory have the same
    structure and corresponding values, must all emit the same DOT code, even
    across separate program runs. No caching is performed across calls to
    draw_extended. As in draw and draw_iterative, empty branches are drawn as
    point nodes, and a graphviz.Digraph is returned.
    """
    return _draw_extended_dag(root) if dag else _draw_extended_faded(root)


__all__ = [thing.__name__ for thing in (
    examples,
    green,
    Node,
    FrozenNode,
    preorder,
    inorder,
    postorder,
    general_dfs,
    levelorder,
    preorder_iterative,
    size,
    size_recursive,
    size_iterative,
    height,
    height_iterative,
    height_iterative_alt,
    copy,
    copy_iterative,
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
    linear_search_mindepth,
    linear_search_mindepth_alt,
    nearest_ancestor,
    is_bst,
    is_bst_alt,
    is_bst_iterative,
    binary_search,
    binary_search_iterative,
    binary_insert,
    binary_insert_iterative,
    build_bst,
    tree_sort,
    find_subtree,
    find_subtree_fast,
    copy_compact,
    draw_extended,
)]
