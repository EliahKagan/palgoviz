"""
Examples of binary trees, for testing and exploration.

Each submodule contains unary functions that take a node-type argument, which
should be a class like tree.Node or tree.FrozenNode. The functions return trees
built from the given node type. All nodes are always newly created, unless the
passed node type itself defines a __new__ method that gives a cached instance.

Tests in test_tree.py depend on these examples.

The most important submodules, in the suggested order of exploration, are:

  1. trivial
  2. basic
  3. bst

There are also some special-purpose submodules:

  4. mirror
  5. bilateral
  6. almost_bst

No two trees produced by distinct factory functions drawn from trivial, basic,
or bst are ever structurally equal. That is, the trivial, basic, and bst
factories are all different from each other. That occasionally does not hold
when the mirror, bilateral, and almost_bst modules are included. As one
example, the mirrored factory for basic.left_chain, mirror.left_chain, is
actually equivalent to bst.right_chain.
"""

__all__ = ['almost_bst', 'basic', 'bilateral', 'bst', 'mirror', 'trivial']

from . import almost_bst, basic, bilateral, bst, mirror, trivial