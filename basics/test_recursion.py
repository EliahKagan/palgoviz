#!/usr/bin/env python

"""Tests for the functions in recursion.py."""

from abc import ABC, abstractmethod
import bisect
import unittest

from parameterized import parameterized, parameterized_class

from compare import OrderIndistinct, Patient, WeakDiamond

from recursion import (
    binary_insertion_sort,
    binary_insertion_sort_recursive,
    binary_insertion_sort_recursive_alt,
    insertion_sort,
    insertion_sort_recursive,
    insertion_sort_recursive_alt,
    insort_left_linear,
    insort_right_linear,
    merge_sort,
    merge_sort_adaptive,
    merge_sort_adaptive_bottom_up,
    merge_sort_bottom_up,
    merge_sort_bottom_up_unstable,
    merge_two,
    merge_two_alt,
    merge_two_slow,
    selection_sort,
    selection_sort_stable,
    sort_by_partitioning,
    sort_by_partitioning_hardened,
    sort_by_partitioning_simple,
)

_NORTH = WeakDiamond.NORTH
_SOUTH = WeakDiamond.SOUTH
_EAST = WeakDiamond.EAST
_WEST = WeakDiamond.WEST


def _build_insort_test_parameters(expected):
    """
    Build insort test cases: old items (as tuple), new item, expected result.

    The old items are given as a tuple so that each run of a test that uses
    them has to make a new list from it. Otherwise tests might contaminate each
    other (and also, even if not, debugging would be hard).
    """
    return [(tuple(expected[:index] + expected[index + 1:]), item, expected)
            for index, item in enumerate(expected)]


class TestInsortAbstract(ABC, unittest.TestCase):
    """Shared tests for insort_left_linear and insert_right_linear."""

    @property
    @abstractmethod
    def implementation(self):
        """The search-and-insert function under test."""

    def test_item_put_into_empty_list(self):
        sorted_items = []
        self.implementation(sorted_items, 42)
        self.assertListEqual(sorted_items, [42])

    def test_low_item_put_in_front_of_singleton_list(self):
        sorted_items = [76]
        self.implementation(sorted_items, 42)
        self.assertListEqual(sorted_items, [42, 76])

    def test_high_item_put_in_back_of_singleton_list(self):
        sorted_items = [42]
        self.implementation(sorted_items, 76)
        self.assertListEqual(sorted_items, [42, 76])

    def test_low_item_put_before_two(self):
        sorted_items = ['B', 'D']
        self.implementation(sorted_items, 'A')
        self.assertListEqual(sorted_items, ['A', 'B', 'D'])

    def test_medium_item_put_between_two(self):
        sorted_items = ['B', 'D']
        self.implementation(sorted_items, 'C')
        self.assertListEqual(sorted_items, ['B', 'C', 'D'])

    def test_high_item_put_after_two(self):
        sorted_items = ['B', 'D']
        self.implementation(sorted_items, 'E')
        self.assertListEqual(sorted_items, ['B', 'D', 'E'])

    def test_lowest_item_put_leftmost_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 0.1)
        self.assertListEqual(sorted_items, [0.1, 12.3, 45.6, 78.9])

    def test_medium_low_item_put_mid_left_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 31.8)
        self.assertListEqual(sorted_items, [12.3, 31.8, 45.6, 78.9])

    def test_medium_high_item_put_mid_right_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 62.7)
        self.assertListEqual(sorted_items, [12.3, 45.6, 62.7, 78.9])

    def test_highest_item_put_rightmost_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 110.2)
        self.assertListEqual(sorted_items, [12.3, 45.6, 78.9, 110.2])

    _NUMBERS = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]

    _WORDS = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    @parameterized.expand(_build_insort_test_parameters(_NUMBERS)
                          + _build_insort_test_parameters(_WORDS))
    def test_new_item_put_in_order_in_several(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)

    @parameterized.expand([
        (range(1, 101), 12, [*range(1, 13), *range(12, 101)]),
        (range(1, 101), 15, [*range(1, 16), *range(15, 101)]),
        (range(1, 101), 79, [*range(1, 80), *range(79, 101)]),
        (range(1, 101), 82, [*range(1, 83), *range(82, 101)]),
    ])
    def test_duplicate_item_put_in_order_in_hundred(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)


class TestInsortLeftAbstract(TestInsortAbstract):
    """Tests for leftmost-point insort functions."""

    def test_incomparable_put_first(self):
        sorted_items = [
            OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
            OrderIndistinct(4), OrderIndistinct(5),
        ]

        expected = [
            OrderIndistinct(6), OrderIndistinct(1), OrderIndistinct(2),
            OrderIndistinct(3), OrderIndistinct(4), OrderIndistinct(5),
        ]

        self.implementation(sorted_items, OrderIndistinct(6))
        self.assertListEqual(sorted_items, expected)

    @parameterized.expand([
        ((_SOUTH, _EAST, _WEST, _NORTH), _EAST,
            [_SOUTH, _EAST, _EAST, _WEST, _NORTH]),
        ((_SOUTH, _EAST, _WEST, _NORTH), _WEST,
            [_SOUTH, _WEST, _EAST, _WEST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _EAST,
            [_SOUTH, _EAST, _WEST, _EAST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _WEST,
            [_SOUTH, _WEST, _WEST, _EAST, _NORTH]),
    ])
    def test_new_weak_item_put_in_order_leftward(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)

    def test_weak_ordered_item_put_left_of_multiple_similars(self):
        sorted_items = [Patient('A', 1), Patient('Z', 2), Patient('B', 3),
                        Patient('Y', 3), Patient('C', 3), Patient('X', 4)]

        new_item = Patient('N', 3)

        expected = sorted_items[:]
        expected.insert(2, new_item)  # It should go at the LEFT of the range.

        self.implementation(sorted_items, new_item)
        self.assertListEqual(sorted_items, expected)


class TestInsortRightAbstract(TestInsortAbstract):
    """Tests for rightmost-point insort functions."""

    def test_incomparable_put_last(self):
        sorted_items = [
            OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
            OrderIndistinct(4), OrderIndistinct(5),
        ]

        expected = [
            OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
            OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6),
        ]

        self.implementation(sorted_items, OrderIndistinct(6))
        self.assertListEqual(sorted_items, expected)

    @parameterized.expand([
        ((_SOUTH, _EAST, _WEST, _NORTH), _EAST,
            [_SOUTH, _EAST, _WEST, _EAST, _NORTH]),
        ((_SOUTH, _EAST, _WEST, _NORTH), _WEST,
            [_SOUTH, _EAST, _WEST, _WEST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _EAST,
            [_SOUTH, _WEST, _EAST, _EAST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _WEST,
            [_SOUTH, _WEST, _EAST, _WEST, _NORTH]),
    ])
    def test_new_weak_item_put_in_order_rightward(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)

    def test_weak_ordered_item_put_right_of_multiple_similars(self):
        sorted_items = [Patient('A', 1), Patient('Z', 2), Patient('B', 3),
                        Patient('Y', 3), Patient('C', 3), Patient('X', 4)]

        new_item = Patient('N', 3)

        expected = sorted_items[:]
        expected.insert(5, new_item)  # It should go at the RIGHT of the range.

        self.implementation(sorted_items, new_item)
        self.assertListEqual(sorted_items, expected)


class TestInsortLeft(TestInsortLeftAbstract):
    """Tests for bisect.insort_left. This is really to test our tests."""

    @property
    def implementation(self):
        return bisect.insort_left


class TestInsortRight(TestInsortRightAbstract):
    """Tests for bisect.insort_right. This is really to test our tests."""

    @property
    def implementation(self):
        return bisect.insort_right


# TODO: Test which, and how many, and what kind, of comparisons are performed.
class TestInsortLeftLinear(TestInsortLeftAbstract):
    """Tests for the insort_left_linear function."""

    @property
    def implementation(self):
        return insort_left_linear


# TODO: Test which, and how many, and what kind, of comparisons are performed.
class TestInsortRightLinear(TestInsortRightAbstract):
    """Tests for the insort_right_linear function."""

    @property
    def implementation(self):
        return insort_right_linear


del TestInsortAbstract, TestInsortLeftAbstract, TestInsortRightAbstract


@parameterized_class(('name', 'function'), [
    (merge_two_slow.__name__, staticmethod(merge_two_slow)),
    (merge_two.__name__, staticmethod(merge_two)),
    (merge_two_alt.__name__, staticmethod(merge_two_alt)),
])
class TestTwoWayMergers(unittest.TestCase):
    """Tests for the two way merge functions."""

    def test_left_first_interleaved_merges(self):
        result = self.function([1, 3, 5], [2, 4, 6])
        self.assertListEqual(result, [1, 2, 3, 4, 5, 6])

    def test_left_first_and_last_interleaved_merges(self):
        result = self.function([1, 3, 7], [2, 4, 6])
        self.assertListEqual(result, [1, 2, 3, 4, 6, 7])

    def test_right_first_interleaved_merges(self):
        result = self.function([2, 4, 6], [1, 3, 5])
        self.assertListEqual(result, [1, 2, 3, 4, 5, 6])

    def test_right_first_and_last_interleaved_merges(self):
        result = self.function([2, 4, 6], [1, 3, 7])
        self.assertListEqual(result, [1, 2, 3, 4, 6, 7])

    def test_empty_list_on_left_gives_right_side(self):
        result = self.function([], [2, 4, 6])
        self.assertListEqual(result, [2, 4, 6])

    def test_empty_tuple_on_left_gives_right_side(self):
        result = self.function((), [2, 4, 6])
        self.assertListEqual(result, [2, 4, 6])

    def test_empty_tuple_with_empty_list_gives_empty_list(self):
        result = self.function((), [])
        self.assertListEqual(result, [])

    def test_empty_list_with_empty_tuple_gives_empty_list(self):
        result = self.function([], ())
        self.assertListEqual(result, [])

    def test_empty_tuple_on_left_gives_right_side_as_list(self):
        """
        Merging an empty tuple with a tuple with duplicate leading items works.
        """
        result = self.function((), (1, 1, 4, 7, 8))
        self.assertListEqual(result, [1, 1, 4, 7, 8])

    def test_empty_tuple_on_right_gives_left_side_as_list(self):
        """
        Merging a tuple with duplicate leading items with an empty tuple works.
        """
        result = self.function((1, 1, 4, 7, 8), ())
        self.assertListEqual(result, [1, 1, 4, 7, 8])

    def test_is_a_stable_merge_when_items_do_not_compare(self):
        lhs = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3)]
        rhs = [OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        expected = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
                    OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        result = self.function(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_is_a_stable_merge_when_items_compare_equal(self):
        lhs = 1
        rhs = 1.0
        r1, r2 = self.function((lhs,), (rhs,))
        with self.subTest(result='r1'):
            self.assertIs(r1, lhs)
        with self.subTest(result='r2'):
            self.assertIs(r2, rhs)

    def test_is_a_stable_merge_when_some_items_compare_equal(self):
        lhs = [WeakDiamond.SOUTH, WeakDiamond.EAST, WeakDiamond.NORTH]
        rhs = [WeakDiamond.WEST, WeakDiamond.WEST]
        expected = [WeakDiamond.SOUTH, WeakDiamond.EAST, WeakDiamond.WEST,
                    WeakDiamond.WEST, WeakDiamond.NORTH]
        result = self.function(lhs, rhs)
        self.assertListEqual(result, expected)


_MERGE_PARAMS = [
    ('no_args', dict()),
    (merge_two_slow.__name__, dict(merge=merge_two_slow)),
    (merge_two.__name__, dict(merge=merge_two)),
    (merge_two_alt.__name__, dict(merge=merge_two_alt)),
]

_ALL_BASIC_SORTS = [
    binary_insertion_sort,
    binary_insertion_sort_recursive,
    binary_insertion_sort_recursive_alt,
    insertion_sort,
    insertion_sort_recursive,
    insertion_sort_recursive_alt,
    selection_sort,
    selection_sort_stable,
]

_STABLE_BASIC_SORTS = [
    binary_insertion_sort,
    binary_insertion_sort_recursive,
    binary_insertion_sort_recursive_alt,
    insertion_sort,
    insertion_sort_recursive,
    insertion_sort_recursive_alt,
    selection_sort_stable,
]

# TODO: Adapt the tests so they can test the in-place sorts, too.

_ALL_MERGESORTS = [
    merge_sort,
    merge_sort_bottom_up_unstable,
    merge_sort_bottom_up,
    merge_sort_adaptive,
    merge_sort_adaptive_bottom_up,
]

_STABLE_MERGESORTS = [
    merge_sort,
    merge_sort_bottom_up,
    merge_sort_adaptive,
    merge_sort_adaptive_bottom_up,
]

_SORTS_BY_PARTITIONING = [  # TODO: Rename with these sorts' common name.
    sort_by_partitioning_simple,
    sort_by_partitioning,
    sort_by_partitioning_hardened,
]


def _make_simple_sort_params(sorts):
    """
    Make (label, sort, kwargs) @parameteried_class params with empty kwargs.

    This is for testing the sorts that don't use dependency injection.
    """
    return [(f'{sort.__name__}', staticmethod(sort), {}) for sort in sorts]


def _make_mergesort_params(sorts):
    """
    Make (label, sort, kwargs) @parameterized_class params for mergesort.

    This passes custom, often nonempty, kwargs to specify the 2-way merger.
    """
    return [(f'{sort.__name__}_{merge_name}', staticmethod(sort), kwargs)
            for sort in sorts for merge_name, kwargs in _MERGE_PARAMS]


_COMBINED_PARAMS_ALL_SORTS = [
    *_make_simple_sort_params(_ALL_BASIC_SORTS),
    *_make_mergesort_params(_ALL_MERGESORTS),
    *_make_simple_sort_params(_SORTS_BY_PARTITIONING),
]

_COMBINED_PARAMS_STABLE_SORTS = [
    *_make_simple_sort_params(_STABLE_BASIC_SORTS),
    *_make_mergesort_params(_STABLE_MERGESORTS),
    *_make_simple_sort_params(_SORTS_BY_PARTITIONING),
]


@parameterized_class(('label', 'sort', 'kwargs'), _COMBINED_PARAMS_ALL_SORTS)
class TestSort(unittest.TestCase):
    """
    Tests for most of the sort functions in recursion.py.

    These do not include tests of stability. For those, see TestSortStability.
    """

    def test_empty_list_sorts(self):
        result = self.sort([], **self.kwargs)
        self.assertListEqual(result, [])

    def test_empty_tuple_sorts(self):
        result = self.sort((), **self.kwargs)
        self.assertListEqual(result, [])

    def test_singleton_sorts(self):
        result = self.sort((2,), **self.kwargs)
        self.assertListEqual(result, [2])

    def test_two_element_sorted_list_is_unchanged(self):
        result = self.sort([10, 20], **self.kwargs)
        self.assertListEqual(result, [10, 20])

    def test_two_element_unsorted_list_is_sorted(self):
        result = self.sort([20, 10], **self.kwargs)
        self.assertListEqual(result, [10, 20])

    def test_two_element_equal_list_is_unchanged(self):
        result = self.sort([3, 3], **self.kwargs)
        self.assertListEqual(result, [3, 3])

    def test_several_ints_are_sorted(self):
        vals = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
        expected = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315,
                    5660]
        result = self.sort(vals, **self.kwargs)
        self.assertListEqual(result, expected)

    def test_several_strings_are_sorted(self):
        vals = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
        expected = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux',
                    'spam']
        result = self.sort(vals, **self.kwargs)
        self.assertListEqual(result, expected)


@parameterized_class(('label', 'sort', 'kwargs'),
                     _COMBINED_PARAMS_STABLE_SORTS)
class TestSortStability(unittest.TestCase):
    """Stability tests for most of the stable sort functions in recursion.py."""

    def test_sort_is_stable(self):
        vals = [0.0, 0, False]
        results = self.sort(vals, **self.kwargs)
        for i, (val, result) in enumerate(zip(vals, results)):
            with self.subTest(index=i):
                self.assertIs(result, val)

    def test_sort_is_stable_with_100_items(self):
        vals = [OrderIndistinct(x) for x in range(100)]
        result = self.sort(vals, **self.kwargs)
        self.assertListEqual(result, vals)


if __name__ == '__main__':
    unittest.main()
