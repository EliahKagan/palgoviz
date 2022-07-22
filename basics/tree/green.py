"""
Binary tree DFS generator functions delegating to tree.dfs, using greenlets.

tree.dfs is a recursive DFS implementation that traverses a binary tree and
does any combination of preorder, inorder, and postorder actions by calling
f_pre, f_in, or f_post functions passed as optional keyword-only arguments.

Since tree.dfs claims to be a generalization of tree.preorder, tree.inorder,
and tree.postorder, it must be possible to make alternative implementations
of them that delegate traversal to tree.dfs. This submodule contains those
implementations. See green.md in this directory for theoretical details.
"""

from greenlet import greenlet as _greenlet

import tree as _tree


def _adapt(produce):
    """Convert a function passing results to a function into a generator."""
    main = _greenlet.getcurrent()
    sub = _greenlet(lambda: produce(receive=main.switch))

    while True:
        result = sub.switch()
        if sub.dead:
            break
        yield result


def preorder_via_general_dfs(root):
    """Preorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.dfs(root, pre_fn=receive))


def inorder_via_general_dfs(root):
    """Inorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.dfs(root, in_fn=receive))


def postorder_via_general_dfs(root):
    """Postorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.dfs(root, post_fn=receive))


__all__ = [thing.__name__ for thing in (
    preorder_via_general_dfs,
    inorder_via_general_dfs,
    postorder_via_general_dfs,
)]
