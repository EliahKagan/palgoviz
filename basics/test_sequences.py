#!/usr/bin/env python

"""Tests for sequences.py."""

from collections.abc import MutableSequence, Sequence
import random
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

        This facilitates an evaluable repr, to make debugging easier, without
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


class _MyInt(int):
    """Specialized integer. For testing equal base and derived instances."""

    __slots__ = ()

    def __repr__(self):
        """Python code representation."""
        return f'{type(self).__name__}({super().__repr__()})'


class TestVec(unittest.TestCase):
    """Tests for the Vec class."""

    def test_class_is_a_mutable_sequence_type(self):
        self.assertTrue(issubclass(Vec, MutableSequence))

    def test_instance_is_mutable_sequence(self):
        vec = Vec(get_buffer=_FixedSizeBuffer)
        self.assertIsInstance(vec, MutableSequence)

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
            r"\AVec\(\['a', 'b'\], get_buffer=<function TestVec\."
            r'test_repr_shows_repr_of_get_buffer_if_lambda\.<locals>\.<lambda>'
            r' at 0x[0-9A-F]+>\)\Z'
        )

        vec = Vec(['a', 'b'], get_buffer=lambda k, x: [x] * k)
        self.assertRegex(repr(vec), expected_repr_pattern)

    def test_repr_shows_repr_of_get_buffer_if_named_function(self):
        def f(k, x):
            return [x] * k

        expected_repr_pattern = (
            r"\AVec\(\['a', 'b'\], get_buffer=<function TestVec\."
            r'test_repr_shows_repr_of_get_buffer_if_named_function\.<locals>\.'
            r'f at 0x[0-9A-F]+>\)\Z'
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

    _parameterize_equal = parameterized.expand([
        ('len0', []),
        ('len1', [10]),
        ('len2', [10, 20]),
        ('len3', [10, 20, 30]),
        ('len4', [10, 20, 30, 40]),
        ('len5', [10, 20, 30, 40, 50]),
    ])

    @_parameterize_equal
    def test_equal_if_same_elements_in_same_order(self, _name, elements):
        lhs = Vec(elements, get_buffer=_FixedSizeBuffer)
        rhs = Vec(elements, get_buffer=_FixedSizeBuffer)
        self.assertEqual(lhs, rhs)

    @_parameterize_equal
    def test_equal_if_equal_base_derived_elements_in_same_order(self, _name,
                                                                values):
        ints = Vec(values, get_buffer=_FixedSizeBuffer)
        derived_ints = Vec(map(_MyInt, values), get_buffer=_FixedSizeBuffer)
        with self.subTest(lhs_type=int, rhs_type=_MyInt):
            self.assertEqual(ints, derived_ints)
        with self.subTest(lhs_type=_MyInt, rhs_type=int):
            self.assertEqual(derived_ints, ints)

    @_parameterize_equal
    def test_equal_if_equal_unrelated_typed_elements_in_same_order(self, _name,
                                                                   values):
        ints = Vec(values, get_buffer=_FixedSizeBuffer)
        floats = Vec(map(float, values), get_buffer=_FixedSizeBuffer)
        with self.subTest(lhs_type=int, rhs_type=float):
            self.assertEqual(ints, floats)
        with self.subTest(lhs_type=float, rhs_type=int):
            self.assertEqual(floats, ints)

    def test_get_buffer_does_not_participate_in_equality_comparison(self):
        vec1 = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec2 = Vec([10, 20, 30], get_buffer=lambda k, x: [x] * k)
        with self.subTest(lhs='vec1', rhs='vec2'):
            self.assertEqual(vec1, vec2)
        with self.subTest(lhs='vec2', rhs='vec1'):
            self.assertEqual(vec2, vec1)

    @parameterized.expand([
        ([], [42]),
        ([42], []),
        ([42], [76]),
        ([1, 7, 3, 5], [1, 7, 5, 3]),
        ([1, 1, 1], [1, 1, 1, 1]),
        ([1, 1, 1, 1], [1, 1, 1]),
        ([10, 20, object(), 40], [10, 20, object(), 40]),
        (['a', 'b', 'c'], ['c', 'b', 'a']),
    ])
    def test_not_equal_if_unequal_or_differently_ordered_elements(self,
                                                                  lhs_elems,
                                                                  rhs_elems):
        lhs = Vec(lhs_elems, get_buffer=_FixedSizeBuffer)
        rhs = Vec(rhs_elems, get_buffer=_FixedSizeBuffer)
        self.assertNotEqual(lhs, rhs)

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

    def test_cannot_get_slice(self):
        expected_message_pattern = r"\Aindex must be 'int', got 'slice'\Z"
        vec = Vec([10, 20, 30, 40, 50], get_buffer=_FixedSizeBuffer)
        with self.assertRaisesRegex(TypeError, expected_message_pattern):
            vec[1:4]

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

    def test_cannot_set_slice(self):
        expected_message_pattern = r"\Aindex must be 'int', got 'slice'\Z"
        vec = Vec([10, 20, 30, 40, 50], get_buffer=_FixedSizeBuffer)

        with self.subTest(rhs_type_that_should_be_irrelevant=list):
            with self.assertRaisesRegex(TypeError, expected_message_pattern):
                vec[1:4] = [21, 31, 41]

        with self.subTest(rhs_type_that_should_be_irrelevant=Vec):
            rhs_vec = Vec([21, 31, 41], get_buffer=_FixedSizeBuffer)
            with self.assertRaisesRegex(TypeError, expected_message_pattern):
                vec[1:4] = rhs_vec

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

    def test_cannot_del_slice(self):
        expected_message_pattern = r"\Aindex must be 'int', got 'slice'\Z"
        vec = Vec([10, 20, 30, 40, 50], get_buffer=_FixedSizeBuffer)
        with self.assertRaisesRegex(TypeError, expected_message_pattern):
            del vec[1:4]

    def test_pop_without_index_pops_last_element(self):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        actual = vec.pop()
        with self.subTest('popped value'):
            self.assertEqual(actual, 30)
        with self.subTest('remaining values'):
            self.assertListEqual(list(vec), [10, 20])

    def test_cannot_pop_without_index_if_empty(self):
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec.pop()

    @parameterized.expand([
        ('idx0', 0, 10, [20, 30]),
        ('idx1', 1, 20, [10, 30]),
        ('idx2', 2, 30, [10, 20]),
    ])
    def test_can_pop_at_nonnegative_index(self, _name,
                                          index, expected, expected_remaining):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        actual = vec.pop(index)
        with self.subTest('popped value'):
            self.assertEqual(actual, expected)
        with self.subTest('remaining values'):
            self.assertListEqual(list(vec), expected_remaining)

    @parameterized.expand([
        ('idxneg1', -1, 30, [10, 20]),
        ('idxneg2', -2, 20, [10, 30]),
        ('idxneg3', -3, 10, [20, 30]),
    ])
    def test_can_pop_at_negative_index(self, _name,
                                       index, expected, expected_remaining):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        actual = vec.pop(index)
        with self.subTest('popped value'):
            self.assertEqual(actual, expected)
        with self.subTest('remaining values'):
            self.assertListEqual(list(vec), expected_remaining)

    @parameterized.expand([
        ('idx3', 3),
        ('idx4', 4),
        ('idx100', 100),
    ])
    def test_cannot_pop_at_nonnegative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec.pop(index)

    @parameterized.expand([
        ('idxneg4', -4),
        ('idxneg5', -5),
        ('idxneg100', -100),
    ])
    def test_cannot_pop_at_negative_out_of_bounds_index(self, _name, index):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(IndexError):
            vec.pop(index)

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
        In a sequence v, it makes sense to insert at 0 to len(v), inclusive.

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

    def test_append_adds_new_element_to_end(self):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec.append(42)
        self.assertListEqual(list(vec), [10, 20, 30, 42])

    @parameterized.expand([
        ('n10', 10),
        ('n1000', 1000),
        ('n50000', 50_000),
    ])
    def test_usable_as_stack_via_append_and_pop(self, _name, count):
        """Items pop in reverse order of append, at any size."""
        prng = random.Random(6183603487360711583)
        expected = []
        actual = []
        vec = Vec(get_buffer=_FixedSizeBuffer)

        for _ in range(count):
            value = prng.randrange(-10**6, 10**6)
            expected.append(value)
            vec.append(value)

        expected.reverse()

        while vec:
            actual.append(vec.pop())

        self.assertListEqual(actual, expected)

    @parameterized.expand([
        ('n10', 10),
        ('n1000', 1000),
        ('n50000', 50_000),
    ])
    def test_append_and_pop_change_len(self, _name, count):
        """len rises and falls with append and pop operations."""
        prng = random.Random(6183603487360711583)
        expected = list(range(1, count + 1)) + list(range(count - 1, -1, -1))
        actual = []
        vec = Vec(get_buffer=_FixedSizeBuffer)

        for _ in range(count):
            vec.append(prng.randrange(-10**6, 10**6))
            actual.append(len(vec))

        while vec:
            vec.pop()  # del[-1] is more idiomatic here, but this tests pop.
            actual.append(len(vec))

        self.assertEqual(actual, expected)

    # FIXME: Test that removal immediately relinquishes the element reference.

    _parameterize_extend_or_inplace_add = parameterized.expand([
        ('0_seq_0', [], lambda: [], []),
        ('0_iter_0', [], lambda: iter([]), []),
        ('0_seq_1', [], lambda: [11], [11]),
        ('0_iter_1', [], lambda: iter([11]), [11]),
        ('0_seq_2', [], lambda: [11, 21], [11, 21]),
        ('0_iter_2', [], lambda: iter([11, 21]), [11, 21]),
        ('0_seq_3', [], lambda: [11, 21, 31], [11, 21, 31]),
        ('0_iter_3', [], lambda: iter([11, 21, 31]), [11, 21, 31]),

        ('1_seq_0', [10], lambda: [], [10]),
        ('1_iter_0', [10], lambda: iter([]), [10]),
        ('1_seq_1', [10], lambda: [21], [10, 21]),
        ('1_iter_1', [10], lambda: iter([21]), [10, 21]),
        ('1_seq_2', [10], lambda: [21, 31], [10, 21, 31]),
        ('1_iter_2', [10], lambda: iter([21, 31]), [10, 21, 31]),
        ('1_seq_3', [10], lambda: [21, 31, 41], [10, 21, 31, 41]),
        ('1_iter_3', [10], lambda: iter([21, 31, 41]), [10, 21, 31, 41]),

        ('2_seq_0', [10, 20], lambda: [], [10, 20]),
        ('2_iter_0', [10, 20], lambda: iter([]), [10, 20]),
        ('2_seq_1', [10, 20], lambda: [31], [10, 20, 31]),
        ('2_iter_1', [10, 20], lambda: iter([31]), [10, 20, 31]),
        ('2_seq_2', [10, 20], lambda: [31, 41], [10, 20, 31, 41]),
        ('2_iter_2', [10, 20], lambda: iter([31, 41]), [10, 20, 31, 41]),
        ('2_seq_3', [10, 20], lambda: [31, 41, 51], [10, 20, 31, 41, 51]),
        ('2_iter_3', [10, 20], lambda: iter([31, 41, 51]),
            [10, 20, 31, 41, 51]),

        ('3_seq_0', [10, 20, 30], lambda: [], [10, 20, 30]),
        ('3_iter_0', [10, 20, 30], lambda: iter([]), [10, 20, 30]),
        ('3_seq_1', [10, 20, 30], lambda: [41], [10, 20, 30, 41]),
        ('3_iter_1', [10, 20, 30], lambda: iter([41]), [10, 20, 30, 41]),
        ('3_seq_2', [10, 20, 30], lambda: [41, 51], [10, 20, 30, 41, 51]),
        ('3_iter_2', [10, 20, 30], lambda: iter([41, 51]),
            [10, 20, 30, 41, 51]),
        ('3_seq_3', [10, 20, 30], lambda: [41, 51, 61],
            [10, 20, 30, 41, 51, 61]),
        ('3_iter_3', [10, 20, 30], lambda: iter([41, 51, 61]),
            [10, 20, 30, 41, 51, 61]),
    ])

    @_parameterize_extend_or_inplace_add
    def test_extend_adds_new_elements_to_end(self, _name, prefix,
                                             suffix_factory, expected):
        vec = Vec(prefix, get_buffer=_FixedSizeBuffer)
        suffix = suffix_factory()
        vec.extend(suffix)
        self.assertListEqual(list(vec), expected)

    @_parameterize_extend_or_inplace_add
    def test_inplace_add_adds_new_elements_to_end(self, _name, prefix,
                                                  suffix_factory, expected):
        vec = Vec(prefix, get_buffer=_FixedSizeBuffer)
        suffix = suffix_factory()
        vec += suffix
        self.assertListEqual(list(vec), expected)

    @parameterized.expand([
        ('lhs0_rhs0', [], [], []),
        ('lhs0_rhs1', [], [11], [11]),
        ('lhs0_rhs2', [], [11, 21], [11, 21]),
        ('lhs0_rhs3', [], [11, 21, 31], [11, 21, 31]),

        ('lhs1_rhs0', [10], [], [10]),
        ('lhs1_rhs1', [10], [21], [10, 21]),
        ('lhs1_rhs2', [10], [21, 31], [10, 21, 31]),
        ('lhs1_rhs3', [10], [21, 31, 41], [10, 21, 31, 41]),

        ('lhs2_rhs0', [10, 20], [], [10, 20]),
        ('lhs2_rhs1', [10, 20], [31], [10, 20, 31]),
        ('lhs2_rhs2', [10, 20], [31, 41], [10, 20, 31, 41]),
        ('lhs2_rhs3', [10, 20], [31, 41, 51], [10, 20, 31, 41, 51]),

        ('lhs3_rhs0', [10, 20, 30], [], [10, 20, 30]),
        ('lhs3_rhs1', [10, 20, 30], [41], [10, 20, 30, 41]),
        ('lhs3_rhs2', [10, 20, 30], [41, 51], [10, 20, 30, 41, 51]),
        ('lhs3_rhs3', [10, 20, 30], [41, 51, 61], [10, 20, 30, 41, 51, 61]),
    ])
    def test_add_concatenates(self, _name, lhs_elems, rhs_elems, expected):
        lhs = Vec(lhs_elems, get_buffer=_FixedSizeBuffer)
        rhs = Vec(rhs_elems, get_buffer=_FixedSizeBuffer)
        result = lhs + rhs
        self.assertListEqual(list(result), expected)

    _parameterize_multiplication = parameterized.expand([
        ('0_by_0', [], 0, []),
        ('0_by_1', [], 1, []),
        ('0_by_2', [], 2, []),
        ('0_by_3', [], 3, []),

        ('1_by_0', [10], 0, []),
        ('1_by_1', [10], 1, [10]),
        ('1_by_2', [10], 2, [10, 10]),
        ('1_by_3', [10], 3, [10, 10, 10]),

        ('2_by_0', [10, 20], 0, []),
        ('2_by_1', [10, 20], 1, [10, 20]),
        ('2_by_2', [10, 20], 2, [10, 20, 10, 20]),
        ('2_by_3', [10, 20], 3, [10, 20, 10, 20, 10, 20]),

        ('3_by_0', [10, 20, 30], 0, []),
        ('3_by_1', [10, 20, 30], 1, [10, 20, 30]),
        ('3_by_2', [10, 20, 30], 2, [10, 20, 30, 10, 20, 30]),
        ('3_by_3', [10, 20, 30], 3, [10, 20, 30, 10, 20, 30, 10, 20, 30]),
    ])

    @_parameterize_multiplication
    def test_multiply_with_int_on_right_repeats(self, _name,
                                                elements, count, expected):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        result = vec * count
        self.assertListEqual(list(result), expected)

    @_parameterize_multiplication
    def test_multiply_with_int_on_left_repeats(self, _name,
                                               elements, count, expected):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        result = count * vec
        self.assertListEqual(list(result), expected)

    @parameterized.expand([
        ('len0', [], []),
        ('len1', [10], [10]),
        ('len2', [10, 20], [20, 10]),
        ('len3', [10, 20, 30], [30, 20, 10]),
        ('len4', [10, 20, 30, 40], [40, 30, 20, 10]),
        ('len5', [10, 20, 30, 40, 50], [50, 40, 30, 20, 10]),
    ])
    def test_reverse_reverses_in_place(self, _name, elements, expected):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        vec.reverse()
        self.assertListEqual(list(vec), expected)

    def test_clear_removes_all_elements(self):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec.clear()
        with self.subTest('bool'):
            self.assertFalse(vec)
        with self.subTest('len'):
            self.assertEqual(len(vec), 0)
        with self.subTest('=='):
            self.assertEqual(vec, Vec(get_buffer=_FixedSizeBuffer))

    def test_copy_returns_equal(self):
        original = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        duplicate = original.copy()
        self.assertEqual(duplicate, original)

    def test_copy_returns_distinct_object(self):
        original = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        duplicate = original.copy()
        self.assertIsNot(duplicate, original)

    def test_copy_makes_shallow_copy(self):
        original = Vec([[], [], []], get_buffer=_FixedSizeBuffer)
        duplicate = original.copy()
        shallow = all(lhs is rhs for lhs, rhs in zip(original, duplicate))
        self.assertTrue(shallow)

    # FIXME: Write the rest of the tests, including of inherited mixins.


if __name__ == '__main__':
    unittest.main()
