"""
Examples of binary trees, for testing and exploration.

Each submodule contains unary functions that take a node-type argument, which
should be a class like tree.Node or tree.FrozenNode. The functions return trees
built from the given node type. All nodes are always newly created, unless the
passed node type itself defines a __new__ method that gives a cached instance.

Tests in test_tree.py depend on these examples.

The suggested order in which to explore the submodules is:

  1. trivial
  2. basic
  3. bst
  4. almost_bst
"""

__all__ = ('almost_bst', 'basic', 'bst', 'trivial')

from . import almost_bst, basic, bst, trivial
