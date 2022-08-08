"""
Examples of class hierarchies and supporting code, for testing and exploration.

This facilitates automatic and manual testing of class_graph.py.
"""

import testing


class A(metaclass=testing.ShortReprMeta):
    """Top class in an inheritance diamond, for testing."""


class B(A):
    """Left class in an inheritance diamond, for testing."""


class C(A):
    """Right class in an inheritance diamond, for testing."""


class D(B, C):
    """Bottom class in an inheritance diamond, for testing."""


def not_object(cls):
    """Filter to omit the object from traversal, for cleaner output."""
    return cls is not object


__all__ = [thing.__name__ for thing in (A, B, C, D, not_object)]
