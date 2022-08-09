"""
Examples of class hierarchies and supporting code, for testing and exploration.

This facilitates automatic and manual testing of class_graph.py.

The examples reside in two submodules:

  1. simple - A simple inheritance diamond.
  2. abc_stubs - Replication of collections.abc inheritance, without methods.
"""

__all__ = ['abc_stubs', 'simple']

from . import abc_stubs, simple
