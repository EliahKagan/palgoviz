"""
Examples and supporting code for automatic or manual testing of class_graph.py.

Conceptually, this should be part of test_class_graph.py. But when doctests are
run by running class_graph.py as a script, there would be an import cycle. By
putting the two modules' shared dependencies in this third module, the import
cycle can be avoided altogether, which is less complicated than coping with it.
"""


class ShortReprMeta(type):
    """Metaclass to use class names as reprs, to improve doctest clarity."""

    def __repr__(self):
        """Represent a class as its bare name."""
        return self.__name__


class A(metaclass=ShortReprMeta):
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
