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


__all__ = [thing.__name__ for thing in (
    Node,
    preorder,
    inorder,
    postorder,
    dfs,
    levelorder,
    preorder_iterative,
    draw,
    draw_iterative,
)]
