#!/usr/bin/env python

"""Tests for sequences.py."""

from collections.abc import Sequence
import unittest

from parameterized import parameterized

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

    The implementation technique used here, a tuple of objects each of which
    has a single rebindable attribute used to hold an element, is probably less
    efficient than just wrapping a list and not providing any methods that can
    change the length. I've done it this way because:

    1. It is immediately clear that no resizing happens.

    2. If something like list is implemented in terms of _FizedSizeBuffer (or
       by dependency injection, where _FixedSizeBuffer can be passed, as in
       Vec), the whole situation is more satisfying than implementing something
       like list using a fixed buffer that is itself implemented using list.
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

    def test_repr_shows_qualname_of_get_buffer_if_class(self):
        class Derived(_FixedSizeBuffer):
            pass

        expected_repr = (
            "Vec(['a', 'b'], get_buffer=TestVec."
            'test_repr_shows_qualname_of_get_buffer_if_class.<locals>.Derived)'
        )

        vec = Vec(['a', 'b'], get_buffer=Derived)
        self.assertEqual(repr(vec), expected_repr)

    def test_repr_shows_repr_of_get_buffer_if_lambda(self):
        expected_repr_pattern = (
            r"Vec\(\['a', 'b'\], get_buffer=<function TestVec\."
            r'test_repr_shows_repr_of_get_buffer_if_lambda\.<locals>\.<lambda>'
            r' at 0x[0-9A-F]+>\)'
        )

        vec = Vec(['a', 'b'], get_buffer=lambda k, x: [x] * k)
        self.assertRegex(repr(vec), expected_repr_pattern)

    def test_repr_shows_repr_of_get_buffer_if_named_function(self):
        def f(k, x):
            return [x] * k

        expected_repr_pattern = (
            r"Vec\(\['a', 'b'\], get_buffer=<function TestVec\."
            r'test_repr_shows_repr_of_get_buffer_if_named_function\.<locals>\.'
            r'f at 0x[0-9A-F]+>\)'
        )

        vec = Vec(['a', 'b'], get_buffer=f)
        self.assertRegex(repr(vec), expected_repr_pattern)

    def test_repr_shows_repr_of_get_buffer_if_instance(self):
        class BufferFactory:
            def __repr__(self):
                return f'{type(self).__name__}()'

            def __call__(self, k, x):
                return [x] * k

        expected_repr = "Vec(['a', 'b'], get_buffer=BufferFactory())"
        vec = Vec(['a', 'b'], get_buffer=BufferFactory())
        self.assertEqual(repr(vec), expected_repr)

    def test_can_iterate_empty(self):
        """Iterating through a Vec of no elements yields nothing."""
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        it = iter(vec)
        with self.assertRaises(StopIteration):
            next(it)

    @parameterized.expand([
        ('len1', [10]),
        ('len2', [10, 20]),
        ('len3', [10, 20, 30]),
        ('len4', [10, 20, 30, 40]),
        ('len5', [10, 20, 30, 40, 50]),
    ])
    def test_can_iterate(self, _name, elements):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        self.assertListEqual(list(vec), elements)

    def test_can_reverse_iterate_empty(self):
        """Iterating in reverse through a Vec of no elements yields nothing."""
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        it = reversed(vec)
        with self.assertRaises(StopIteration):
            next(it)

    @parameterized.expand([
        ('len1', [10], [10]),
        ('len2', [10, 20], [20, 10]),
        ('len3', [10, 20, 30], [30, 20, 10]),
        ('len4', [10, 20, 30, 40], [40, 30, 20, 10]),
        ('len5', [10, 20, 30, 40, 50], [50, 40, 30, 20, 10]),
    ])
    def test_can_reverse_iterate(self, _name, elements, expected):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        self.assertListEqual(list(reversed(vec)), expected)

    @parameterized.expand([
        ('idx0', 0, 10),
        ('idx1', 1, 20),
        ('idx2', 2, 30),
    ])
    def test_can_get_at_nonnegative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        self.assertEqual(vec[index], expected)

    @parameterized.expand([
        ('idxneg1', -1, 30),
        ('idxneg2', -2, 20),
        ('idxneg3', -3, 10),
    ])
    def test_can_get_at_negative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        self.assertEqual(vec[index], expected)

    @parameterized.expand([
        ('idx3', 3),
        ('idx4', 4),
        ('idx100', 100),
    ])
    def test_cannot_get_at_nonnegative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec[index]

    @parameterized.expand([
        ('idxneg4', -4),
        ('idxneg5', -5),
        ('idxneg100', -100),
    ])
    def test_cannot_get_at_negative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec[index]

    @parameterized.expand([
        ('idx0', 0, [42, 20, 30]),
        ('idx1', 1, [10, 42, 30]),
        ('idx2', 2, [10, 20, 42]),
    ])
    def test_can_set_at_nonnegative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec[index] = 42
        with self.subTest('get value'):
            self.assertEqual(vec[index], 42)
        with self.subTest('iterate'):
            self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('idxneg1', -1, [10, 20, 42]),
        ('idxneg2', -2, [10, 42, 30]),
        ('idxneg3', -3, [42, 20, 30]),
    ])
    def test_can_set_at_negative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec[index] = 42
        with self.subTest('get value'):
            self.assertEqual(vec[index], 42)
        with self.subTest('iterate'):
            self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('idx3', 3),
        ('idx4', 4),
        ('idx100', 100),
    ])
    def test_cannot_set_at_nonnegative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec[index] = 42

    @parameterized.expand([
        ('idxneg4', -4),
        ('idxneg5', -5),
        ('idxneg100', -100),
    ])
    def test_cannot_set_at_negative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec[index] = 42

    @parameterized.expand([
        ('idx0', 0, [20, 30]),
        ('idx1', 1, [10, 30]),
        ('idx2', 2, [10, 20]),
    ])
    def test_can_del_at_nonnegative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        del vec[index]
        self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('idxneg1', -1, [10, 20]),
        ('idxneg2', -2, [10, 30]),
        ('idxneg3', -3, [20, 30]),
    ])
    def test_can_del_at_negative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        del vec[index]
        self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('idx3', 3),
        ('idx4', 4),
        ('idx100', 100),
    ])
    def test_cannot_del_at_nonnegative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            del vec[index]

    @parameterized.expand([
        ('idxneg4', -4),
        ('idxneg5', -5),
        ('idxneg100', -100),
    ])
    def test_cannot_del_at_negative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            del vec[index]

    @parameterized.expand([
        ('idx0', 0, [42, 10, 20, 30]),
        ('idx1', 1, [10, 42, 20, 30]),
        ('idx2', 2, [10, 20, 42, 30]),
        ('idx3', 3, [10, 20, 30, 42]),
    ])
    def test_can_insert_at_nonnegative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec.insert(index, 42)
        with self.subTest('get value'):
            self.assertEqual(vec[index], 42)
        with self.subTest('iterate'):
            self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('idxneg1', -1, [10, 20, 42, 30]),
        ('idxneg2', -2, [10, 42, 20, 30]),
        ('idxneg3', -3, [42, 10, 20, 30]),
    ])
    def test_can_insert_at_negative_index(self, _name, index, expected):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec.insert(index, 42)
        with self.subTest('get value'):
            self.assertEqual(vec[index - 1], 42)
        with self.subTest('iterate'):
            self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('idx4', 4),  # Start at 4, because 3 is a valid insertion index.
        ('idx5', 5),
        ('idx100', 100),
    ])
    def test_cannot_insert_at_nonnegative_out_of_bounds_index(self, _name,
                                                              index):
        """
        In a sequence v, 0 to len(v), inclusive, make sense to insert at.

        Although len(v) - 1 is the highest index we can get, set, or delete at,
        we can insert there, and doing so has the same effect as appending. All
        indices from 0 to and including len(v) are distinct insertion points.

        In Python it's common to allow insertion "at" higher indices, with the
        same effect as inserting at len(v). list and collections.deque support
        this, and it is usually best to support it in one's own types, for
        consistency with the standard library. For now, we prohibit this, to
        illustrate which insertion points are actually meaningful, and to show
        that mixin methods supplied by MutableSequence don't rely on it.
        """
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec.insert(index, 42)

    @parameterized.expand([
        ('idxneg4', -4),
        ('idxneg5', -5),
        ('idxneg100', -100),
    ])
    def test_cannot_insert_at_negative_out_of_bounds_index(self, _name, index):
        """
        In a sequence v, -len(v) to -1, inclusive, make sense to insert at.

        Insertion into any position except the very end can be done by negative
        indices; they mean the same as when used to get, set, and delete.

        In Python it's common to allow insertion "at" even lower indices, with
        the same effect as inserting at -len(v). list and collections.deque
        support this, and it is usually best to support it in one's own types,
        for consistency with the standard library. For now, we prohibit this,
        to illustrate which insertion points are actually meaningful, and to
        show that mixin methods supplied by MutableSequence don't rely on it.
        """
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec.insert(index, 42)

    # FIXME: Write the rest of the tests, including of inherited mixins.


if __name__ == '__main__':
    unittest.main()
