"""Simple examples of class hierarchies."""

import testing as _testing


class A(metaclass=_testing.ShortReprMeta):
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
