#!/usr/bin/env python

"""Tests for sequences.py."""

from collections.abc import Sequence
import unittest

from sequences import Vec


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

        This facilitates an evaluable repr, to makee debugging easier, without
        allowing the _FixedSizeBuffer class itself to be called with element
        values, which, if allowed, might let tests pass that should fail.
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

    def test_cannot_construct_without_get_buffer_arg(self):
        with self.assertRaises(TypeError):
            Vec()

    def test_cannot_construct_with_positional_get_buffer_arg(self):
        with self.assertRaises(TypeError):
            Vec(_FixedSizeBuffer)

    def test_can_construct_with_only_get_buffer_keyword_arg(self):
        try:
            Vec(get_buffer=_FixedSizeBuffer)
        except TypeError as error:
            self.fail(f'construction failed: {error}')

    def test_can_construct_with_empty_list(self):
        try:
            Vec([], get_buffer=_FixedSizeBuffer)
        except TypeError as error:
            self.fail(f'construction failed: {error}')

    def test_can_construct_with_nonempty_list(self):
        try:
            Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        except TypeError as error:
            self.fail(f'construction failed: {error}')

    def test_can_construct_with_empty_generator(self):
        try:
            Vec((x for x in ()), get_buffer=_FixedSizeBuffer)
        except TypeError as error:
            self.fail(f'construction failed: {error}')

    def test_can_construct_with_nonempty_generator(self):
        try:
            Vec((x for x in (10, 20, 30)), get_buffer=_FixedSizeBuffer)
        except TypeError as error:
            self.fail(f'construction failed: {error}')

    def test_falsy_on_construction_without_iterable(self):
        vec = Vec(get_buffer=_FixedSizeBuffer)
        self.assertFalse(vec)

    def test_falsy_on_construction_with_empty_list(self):
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        self.assertFalse(vec)

    def test_truthy_on_construction_with_singleton_list(self):
        vec = Vec([10], get_buffer=_FixedSizeBuffer)
        self.assertTrue(vec)

    def test_truthy_on_construction_with_multiple_item_list(self):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        self.assertTrue(vec)

    def test_falsy_on_construction_with_empty_generator(self):
        vec = Vec((x for x in ()), get_buffer=_FixedSizeBuffer)
        self.assertFalse(vec)

    def test_truthy_on_construction_with_singleton_generator(self):
        vec = Vec((x for x in (10,)), get_buffer=_FixedSizeBuffer)
        self.assertTrue(vec)

    def test_truthy_on_construction_with_multiple_item_generator(self):
        vec = Vec((x for x in (10, 20, 30)), get_buffer=_FixedSizeBuffer)
        self.assertTrue(vec)

    def test_len_0_on_construction_without_iterable(self):
        vec = Vec(get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 0)

    def test_len_0_on_construction_with_empty_list(self):
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 0)

    def test_len_1_on_construction_with_singleton_list(self):
        vec = Vec([10], get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 1)

    def test_len_accurate_on_construction_with_multiple_item_list(self):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 3)

    def test_len_0_on_construction_with_empty_generator(self):
        vec = Vec((x for x in ()), get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 0)

    def test_len_1_on_construction_with_singleton_generator(self):
        vec = Vec((x for x in (10,)), get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 1)

    def test_len_accurate_on_construction_with_multiple_item_generator(self):
        vec = Vec((x for x in (10, 20, 30)), get_buffer=_FixedSizeBuffer)
        self.assertEqual(len(vec), 3)

    def test_repr_shows_no_elements_on_construction_without_iterable(self):
        expected_repr = 'Vec([], get_buffer=_FixedSizeBuffer)'
        vec = Vec(get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_no_elements_on_construction_with_empty_list(self):
        expected_repr = 'Vec([], get_buffer=_FixedSizeBuffer)'
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_element_on_construction_with_singleton_list(self):
        expected_repr = 'Vec([10], get_buffer=_FixedSizeBuffer)'
        vec = Vec([10], get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_elements_on_construction_with_multiple_item_list(self):
        expected_repr = 'Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)'
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_no_elements_on_construction_with_empty_generator(self):
        expected_repr = 'Vec([], get_buffer=_FixedSizeBuffer)'
        vec = Vec((x for x in ()), get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_element_on_construction_with_singleton_generator(self):
        expected_repr = 'Vec([10], get_buffer=_FixedSizeBuffer)'
        vec = Vec((x for x in (10,)), get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_elements_on_construction_with_multiple_item_generator(
            self):
        expected_repr = 'Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)'
        vec = Vec((x for x in (10, 20, 30)), get_buffer=_FixedSizeBuffer)
        self.assertEqual(repr(vec), expected_repr)

    # FIXME: Write the rest of the tests, including of inherited mixins.


if __name__ == '__main__':
    unittest.main()
