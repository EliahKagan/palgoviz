# Copyright (c) 2022 Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Binary tree DFS generator functions delegating to tree.general_dfs.

This module's functions use greenlets. See green.md for details and theory.

tree.general_dfs is a recursive DFS implementation that traverses a binary tree
and does any combination of preorder, inorder, and postorder actions by calling
f_pre, f_in, or f_post functions passed as optional keyword-only arguments.

For the claim that general_dfs generalizes preorder, inorder, and postorder to
be true, it must be possible to make alternative implementations of those three
generator functions that delegate traversal to general_dfs. That is done here.
"""

__all__ = [
    'preorder_via_general_dfs',
    'inorder_via_general_dfs',
    'postorder_via_general_dfs',
]

from greenlet import greenlet as _greenlet

from palgoviz import tree as _tree


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
    return _adapt(lambda receive: _tree.general_dfs(root, pre_fn=receive))


def inorder_via_general_dfs(root):
    """Inorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.general_dfs(root, in_fn=receive))


def postorder_via_general_dfs(root):
    """Postorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.general_dfs(root, post_fn=receive))
