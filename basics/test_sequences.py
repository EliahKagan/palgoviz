#!/usr/bin/env python

"""Tests for sequences.py."""

from collections.abc import MutableSequence, Sequence
import fractions
import inspect
import math
import random
import unittest
import weakref

from parameterized import parameterized

from sequences import Vec
import testing


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

    2. If something like list is implemented in terms of _FixedSizeBuffer (or
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
        instance._cells = tuple(testing.Cell(value) for value in values)
        return instance

    def __init__(self, length, default):
        """Create a default value filled buffer of the given length."""
        self._cells = tuple(testing.Cell(default) for _ in range(length))

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


class _NonSelfEqual:
    """
    Pathological object that is not even equal to itself.

    Objects can, in nearly all cases, be assumed equal to themselves. When a
    non-self-equal object, such as instances of this class, does exist, it is
    usually the responsibility of the the code that introduces such an object
    to ensure it is never used in any ways that would cause problems. But there
    are a few situations where one ought to make specific guarantees about the
    handling of such objects, because floating point NaNs have this property.

    The purpose of this class is to facilitate tests of behaviors that hold for
    NaN values, including but not limited to math.nan, to ensure NaNs aren't
    special-cased by accident. If you decide to special-case NaNs, don't test
    with this. (Other than NaNs and for testing, there is probably never a good
    justification for introducing an object that compares unequal to itself.)
    """

    __slots__ = ()

    def __repr__(self):
        """Python code representation for debugging."""
        return f'{type(self).__name__}()'

    def __eq__(self, _):
        """A _NonSelfEqual instance is never equal to anything, even itself."""
        return False


# FIXME: As currently written, these tests verify no time or space complexity
# guarantees, which would be tricky to do. It is easier, and more helpful for
# finding bugs, to test that capacity changes as expected, and that the change
# in underlying representation (that is, in the objects, and their arrangement,
# that constitute the state of the data structure) is as expected across a
# change in capacity. But neither capacity nor underlying representation are
# documented. To verify correctness, do any TWO of the following three things:
#
#   (1) Write test case methods to cover this. The specifics of what they
#       assert will be determined by design choices you made that need not
#       otherwise be documented and that users must not rely on. (You can still
#       change these aspects of the design at any time, so long as you also
#       change the tests accordingly.) They can go in this class or in another
#       class in this test module. Wherever your put them, clearly document
#       that users must not rely on claims they make. This is important because
#       unit tests serve a secondary purpose as documentation; users are
#       usually justified in relying on claims they test. Except when a test is
#       clearly specific to a private module, class, or function, unit tests
#       that intend not to make public guarantees should state that explicitly.
#
#   (2) Manually test this in a notebook. Try out enough cases to give a
#       convincing demonstration of correctness. Inspect the private state of
#       one or more Vec objects. (The point is to check that this private state
#       is operated on in the way you intend.) Give the notebook filename in an
#       appropriate docstring in this module. Unless there is strong reason for
#       it to go elsewhere instead, that should be the TestVec class docstring.
#
#   (3) Try out a fairly small but nontrivial series of operations on one or
#       more Vec objects on https://pythontutor.com, to inspect and visualize
#       the changes in underlying representation, step by step. You can paste
#       the whole Vec class, with its docstring removed or abridged, there.
#       Because Python Tutor uses an older version of Python and doesn't work
#       with all language and library features, you may have to make changes to
#       get it to work there. (Please do not deliberately limit yourself in
#       sequences.py to features that work on Python Tutor. But there is a
#       fairly good chance few or no modifications will be needed.) Create a
#       permalink to the code/visualization on Python Tutor and give it in an
#       appropriate docstring in this module. Unless there is strong reason for
#       it to go elsewhere instead, that should be the TestVec class docstring.
#
# Having done two of those things to verify that the underlying representation
# changes when, and in the specific way, that you intend, including changes in
# capacity, delete this fixme comment, to avoid wrongly claiming that something
# believed to be complete and correct is unfinished. But you may want to tag
# the last commit that has this, since you may want to look at it again in a
# future exercise in which Vec is modified to shrink as well as grow capacity.
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
            r' at 0x(?:[0-9A-F]+|[0-9a-f]+)>\)\Z'
        )

        vec = Vec(['a', 'b'], get_buffer=lambda k, x: [x] * k)
        self.assertRegex(repr(vec), expected_repr_pattern)

    def test_repr_shows_repr_of_get_buffer_if_named_function(self):
        def f(k, x):
            return [x] * k

        expected_repr_pattern = (
            r"\AVec\(\['a', 'b'\], get_buffer=<function TestVec\."
            r'test_repr_shows_repr_of_get_buffer_if_named_function\.<locals>\.'
            r'f at 0x(?:[0-9A-F]+|[0-9a-f]+)>\)\Z'
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

    @parameterized.expand([
        ('math_nan', math.nan),
        ('inf_minus_inf', math.inf - math.inf),
    ])
    def test_non_self_equal_nan_does_not_prevent_equality(self, _name, nan):
        """Like list and tuple, Vec treats NaN objects as if self-equal."""
        if nan == nan:
            raise Exception("platform has non-pathological NaN, can't test")
        lhs = Vec([10, 20, nan, 30], get_buffer=_FixedSizeBuffer)
        rhs = Vec([10, 20, nan, 30], get_buffer=_FixedSizeBuffer)
        self.assertEqual(lhs, rhs)

    def test_nonidentical_nans_are_distinguished(self):
        """Only the same NaN object is treated as if equal to itself."""
        lhs_nan = math.nan
        rhs_nan = math.inf - math.inf
        if lhs_nan == rhs_nan:
            raise Exception('very weird (broken?) floating point NaN equality')
        lhs = Vec([10, 20, lhs_nan, 30], get_buffer=_FixedSizeBuffer)
        rhs = Vec([10, 20, rhs_nan, 30], get_buffer=_FixedSizeBuffer)
        self.assertNotEqual(lhs, rhs)

    def test_self_unequal_non_nan_does_not_prevent_equality(self):
        """
        Non-self-equal objects are treated as if self-equal, even if not NaN.

        There are probably never any good use cases, other than NaN, of objects
        unequal to themselves (besides tests like this). But Vec doesn't treat
        NaN specially. Other such pathological objects are treated similarly.
        """
        element = _NonSelfEqual()
        if element == element:
            raise Exception('bug in test helper')
        lhs = Vec([10, 20, element, 30], get_buffer=_FixedSizeBuffer)
        rhs = Vec([10, 20, element, 30], get_buffer=_FixedSizeBuffer)
        self.assertEqual(lhs, rhs)

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

    def test_del_at_end_immediately_relinquishes_element_references(self):
        """
        Deleting from the end removes the reference from the container.

        No matter where an element is, removing it from the container should
        leave no dangling reference to it, so the container doesn't needlessly
        keep it from being garbage collected. But the case of removing from the
        end is the easiest to test of the situations where bugs may arise.
        """
        elements = (testing.WRCell(i) for i in range(17))
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        weak = [weakref.ref(x) for x in vec]

        for r in reversed(weak):
            with self.subTest(number=r().value):  # Show the "boxed" number.
                del vec[-1]
                testing.collect_if_not_ref_counting()
                self.assertIsNone(r())

    @parameterized.expand([
        ('n1', 1),
        ('n2', 2),
        ('n3', 3),
        ('n4', 4),
        ('n5', 5),
        ('n6', 6),
        ('n7', 7),
        ('n8', 8),
        ('n9', 9),
        ('n10', 10),
        ('n11', 11),
        ('n12', 12),
        ('n13', 13),
        ('n14', 14),
        ('n15', 15),
        ('n16', 16),
    ])
    def test_del_relinquishes_last_reference_to_moved_element(self, _name, n):
        """
        Extra references are not kept to elements moved by a previous deletion.

        Deleting a non-rightmost element moves at least one element to the left
        to fill the hole. Some ways of implementing this introduce a bug where
        an extra reference is kept to some other element. Then, if that other
        element is removed or replaced, the data structure may still hold that
        extra reference to it, preventing it from being garbage collected until
        the whole data structure itself is eligible for garbage collection.

        People are often surprised to learn memory leaks are possible even in
        languages with automatic garbage collection (e.g., Python, Java, C#).
        Garbage collection is very useful, but it doesn't free programmers from
        the need to avoid long-lived references from objects that are still in
        use to objects that are intended never to be used again.
        """
        vec = Vec(range(17), get_buffer=_FixedSizeBuffer)
        vec[-1] = testing.WeakReferenceable()
        for _ in range(n):
            del vec[0]
        r = weakref.ref(vec[-1])
        vec[-1] = 42  # We can assign anything here, besides vec[-1] itself.
        self.assertIsNone(r())

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
    def test_vec_times_int_repeats(self, _name, elements, count, expected):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        result = vec * count
        self.assertListEqual(list(result), expected)

    @_parameterize_multiplication
    def test_int_times_vec_repeats(self, _name, elements, count, expected):
        vec = Vec(elements, get_buffer=_FixedSizeBuffer)
        result = count * vec
        self.assertListEqual(list(result), expected)

    def test_in_operator_returns_false_if_empty(self):
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        self.assertNotIn(50, vec)

    def test_in_operator_returns_false_if_absent(self):
        vec = Vec([30, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        self.assertNotIn(42, vec)

    def test_in_operator_returns_true_if_present(self):
        vec = Vec([30, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        self.assertIn(50, vec)

    def test_in_operator_returns_true_if_multiple_present(self):
        vec = Vec([30, 50, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        self.assertIn(50, vec)

    def test_index_on_empty_raises(self):
        """index raises ValueError if there are no values to search in."""
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.index(42)

    def test_index_of_absent_raises(self):
        """index raises ValueError if no equal value is found."""
        vec = Vec([30, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.index(42)

    def test_index_of_present_finds_index(self):
        """index returns an index to the equal value when present."""
        vec = Vec([30, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        result = vec.index(50)
        self.assertEqual(result, 2)

    def test_index_of_present_finds_first_index(self):
        """index returns an index to the first of multiple equal values."""
        values = [30, 20, 50, 10, 30, 20, 50, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        result = vec.index(50)
        self.assertEqual(result, 2)

    def test_index_with_start_skips_prefix_then_if_absent_raises(self):
        """index raises ValueError if no equal value after start is found."""
        vec = Vec([30, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.index(50, 3)

    def test_index_with_start_skips_prefix_then_if_present_finds_index(self):
        """index returns an index to the equal value after a skipped prefix."""
        vec = Vec([30, 20, 50, 10, 40], get_buffer=_FixedSizeBuffer)
        result = vec.index(50, 2)
        self.assertEqual(result, 2)

    def test_index_with_start_skips_prefix_then_if_present_finds_first_index(
            self):
        """
        index returns an index to the first of multiple equal values after a
        skipped prefix.
        """
        values = [30, 20, 50, 10, 30, 20, 50, 10, 30, 20, 50, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        result = vec.index(50, 3)
        self.assertEqual(result, 6)

    def test_index_start_to_end_of_absent_in_slice_raises(self):
        """
        index raises ValueError if no equal value in vec[start:end] is found.

        This notation is merely illustrative, since while most sequences should
        and do support slicing, Vec does not.
        """
        values = [30, 20, 50, 10, 30, 20, 50, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.index(50, 3, 6)

    def test_index_start_to_end_of_present_in_slice_finds_index(self):
        """
        index returns an index to the equal value in vec[start:end].

        This notation is merely illustrative, since while most sequences should
        and do support slicing, Vec does not.
        """
        values = [30, 20, 50, 10, 30, 20, 50, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        result = vec.index(50, 2, 6)
        self.assertEqual(result, 2)

    def test_index_start_to_end_of_present_in_slice_finds_first_index(self):
        """
        index returns an index to the first of multiple equal values in
        vec[start:end].

        This notation is merely illustrative, since while most sequences should
        and do support slicing, Vec does not.
        """
        values = [30, 20, 50, 10, 30, 20, 50, 10,
                  30, 20, 50, 10, 30, 20, 50, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        result = vec.index(50, 3, 12)
        self.assertEqual(result, 6)

    def test_index_finds_equal_value_of_different_type(self):
        values = [50.0, 40.0, 30.0, 20.0, 10.0, 50, 40, 30, 20, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        result = vec.index(20)
        self.assertEqual(result, 3)

    @parameterized.expand([
        ('math_nan', math.nan),
        ('inf_minus_inf', math.inf - math.inf),
    ])
    def test_index_finds_non_self_equal_nan(self, _name, nan):
        """Like list and tuple, Vec treats NaN objects as if self-equal."""
        if nan == nan:
            raise Exception("platform has non-pathological NaN, can't test")
        vec = Vec([10, 20, nan, 30], get_buffer=_FixedSizeBuffer)
        result = vec.index(nan)
        self.assertEqual(result, 2)

    def test_index_does_not_find_nonidentical_nan(self):
        """Only the same NaN object is treated as if equal to itself."""
        absent_nan = math.nan
        present_nan = math.inf - math.inf
        if absent_nan == present_nan:
            raise Exception('very weird (broken?) floating point NaN equality')
        vec = Vec([10, 20, present_nan, 30], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.index(absent_nan)

    def test_index_finds_self_unequal_non_nan(self):
        """
        Non-self-equal objects are treated as if self-equal, even if not NaN.

        See test_self_unequal_non_nan_does_not_prevent_equality for details.
        """
        element = _NonSelfEqual()
        if element == element:
            raise Exception('bug in test helper')
        vec = Vec([10, 20, element, 30], get_buffer=_FixedSizeBuffer)
        result = vec.index(element)
        self.assertEqual(result, 2)

    def test_count_returns_zero_if_empty(self):
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        result = vec.count(10)
        self.assertEqual(result, 0)

    def test_count_returns_zero_if_absent(self):
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        result = vec.count(42)
        self.assertEqual(result, 0)

    def test_count_counts_equal_occurrences(self):
        values = 'qhibxeukgmqefsjfyjwyjdzahdexuejkemjtulsfbfqawarcah'
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        if len(vec) != len(values):
            raise Exception("incorrect construction, can't test count")
        result = vec.count('a')
        self.assertEqual(result, 4)

    def test_count_counts_equal_occurrences_even_of_different_types(self):
        values = [3, 2, 1, 0, fractions.Fraction(2, 1), 4.0, 2.0, 3.0, 1.0]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        result = vec.count(2.0)
        self.assertEqual(result, 3)

    def test_remove_raises_if_empty(self):
        """remove raises ValueError if there are no values to search in."""
        vec = Vec([], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.remove(20)

    def test_remove_raises_if_absent(self):
        """remove raises ValueError if no equal value is found."""
        vec = Vec([30, 10, 50, 40], get_buffer=_FixedSizeBuffer)
        with self.assertRaises(ValueError):
            vec.remove(20)

    def test_remove_deletes_equal_value_if_present(self):
        """remove removes the equal value if there is one."""
        vec = Vec([30, 10, 20, 50, 40], get_buffer=_FixedSizeBuffer)
        vec.remove(20)
        self.assertListEqual(list(vec), [30, 10, 50, 40])

    def test_remove_deletes_first_equal_value_if_present(self):
        """remove removes the first of multiple equal values."""
        values = [30, 20, 50, 10, 30, 20, 50, 10]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        vec.remove(50)
        self.assertListEqual(list(vec), [30, 20, 10, 30, 20, 50, 10])

    def test_remove_deletes_first_equal_value_even_if_of_different_type(self):
        expected = [3, 1, 0, fractions.Fraction(2, 1), 4.0, 2.0, 3.0, 1.0]
        values = [3, 2, 1, 0, fractions.Fraction(2, 1), 4.0, 2.0, 3.0, 1.0]
        vec = Vec(values, get_buffer=_FixedSizeBuffer)
        vec.remove(fractions.Fraction(2, 1))
        self.assertListEqual(list(vec), expected)

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

    def test_cleared_equals_new_empty(self):
        expected = Vec(get_buffer=_FixedSizeBuffer)
        vec = Vec([10, 20, 30], get_buffer=_FixedSizeBuffer)
        vec.clear()
        self.assertEqual(vec, expected)

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

    # TODO: In the future, we will add a sort method.

    @parameterized.expand([
        ('__contains__',),
        ('__iter__',),
        ('__reversed__',),
        ('index',),
        ('count',),
        ('append',),
        ('reverse',),
        ('extend',),
        ('pop',),
        ('remove',),
        ('__iadd__',),
    ])
    def test_applicable_mixins_are_used(self, name):
        actual = getattr(Vec, name)
        expected = getattr(MutableSequence, name)
        self.assertIs(actual, expected)

    def test_cannot_create_new_attributes(self):
        vec = Vec(get_buffer=_FixedSizeBuffer)
        with self.assertRaises(AttributeError):
            vec.a = 10

    def test_no_public_attributes_besides_instance_methods(self):
        """
        All attributes from dir have leading underscores or are bound methods.

        Calling dir on the instance is imperfect, since it is possible for
        attributes, particularly if they are dynamically generated without
        corresponding dir customizations, to be omitted. But it is pretty good.
        """
        vec = Vec(get_buffer=_FixedSizeBuffer)

        attribute_values = [getattr(vec, name) for name in dir(vec)
                            if not name.startswith('_')]

        self.assertTrue(all(inspect.ismethod(v) for v in attribute_values))


if __name__ == '__main__':
    unittest.main()
