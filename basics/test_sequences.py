#!/usr/bin/env python

"""Tests for sequences.py."""

from collections.abc import Sequence
import unittest


class _Cell:
    """A box holding an object, supporting reassignment."""

    __slots__ = ('value',)

    def __init__(self, value):
        """Create a cell with the given starting value."""
        self.value = value

    def __repr__(self):
        """Code-like representation, for debugging."""
        return f'{type(self).__name__}({self.value!r})'


def _check_index(index):
    """Check that an index has a correct type."""
    if not isinstance(index, int):
        typename = type(index).__name__
        raise TypeError(f"index must be 'int', got {typename!r}")


class _FixedSizeBuffer(Sequence):
    """
    A fixed-length sequence of objects of any type. Supports __setitem__.

    This is meant for testing types that consume a fixed-size buffer.
    """

    __slots__ = ('_cells',)

    @classmethod
    def of(cls, *values):
        """
        Named constructor to build a _FixedSizeBuffer from its arguments.

        This allows a Python-code repr, which may make debugging easier, while
        not allowing the class to be called this way, which could make tests
        pass that ought to fail.
        """
        instance = super().__new__(cls)
        instance._cells = tuple(_Cell(value) for value in values)
        return instance

    def __init__(self, length, default):
        """Create a default value filled buffer of the given length."""
        self._cells = tuple(_Cell(default) for _ in range(length))

    def __repr__(self):
        """Python code representation of this _FixedSizeBuffer instance."""
        delimited_args = ', '.join(repr(cell.value) for cell in self._cells)
        return f'{type(self).__name__}.of({delimited_args})'

    def __len__(self):
        """The number of elements. This never changes in the same instance."""
        return len(self._cells)

    def __getitem__(self, index):
        """Get an item at an index. Slicing is not supported."""
        _check_index(index)
        return self._cells[index].value

    def __setitem__(self, index, value):
        """Set an item at an index. Slicing is not supported."""
        _check_index(index)
        self._cells[index].value = value


class TestVec(unittest.TestCase):
    """Tests for the Vec class."""

    # !!FIXME: Write all test cases except those that are an exercise to write.

    # FIXME: Write test cases for the functionality of all methods inherited
    # directly or indirectly from MutableSequence, both abstract and concrete.


if __name__ == '__main__':
    unittest.main()
