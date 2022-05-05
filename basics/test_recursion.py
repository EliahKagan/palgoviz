#!/usr/bin/env python

"""Tests for the functions in recursion.py."""

import unittest

from parameterized import parameterized_class, parameterized, param

from compare import OrderIndistinct, WeakDiamond
from recursion import merge_sort, merge_two, merge_two_alt, merge_two_slow


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


class TestMergeSort(unittest.TestCase):
    """Tests for the merge_sort function."""

    @parameterized.expand([
        param('no_arg'),
        param(merge_two_slow.__name__, merge=merge_two_slow),
        param(merge_two.__name__, merge=merge_two),
        param(merge_two_alt.__name__, merge=merge_two_alt),
    ])
    def test_empty_list_sorts(self, _name, **kwargs):
        result = merge_sort([], **kwargs)
        self.assertEqual(result, [])

    def test_empty_tuple_sorts(self):
        result = merge_sort(())
        self.assertEqual(result, [])

    def test_singleton_sorts(self):
        result = merge_sort((2,))
        self.assertEqual(result, [2])

    def test_two_element_sorted_list_is_unchanged(self):
        result = merge_sort([10, 20])
        self.assertEqual(result, [10, 20])

    def test_two_element_unsorted_list_is_sorted(self):
        result = merge_sort([20, 10])
        self.assertEqual(result, [10, 20])

    def test_two_element_equal_list_is_unchanged(self):
        result = merge_sort([3, 3])
        self.assertEqual(result, [3, 3])

    def test_several_ints_are_sorted(self):
        vals = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
        expected = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
        result = merge_sort(vals)
        self.assertEqual(result, expected)

    def test_several_strings_are_sorted(self):
        vals = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
        expected = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
        result = merge_sort(vals)
        self.assertEqual(result, expected)

    def test_sort_is_stable(self):
        vals = [0.0, 0, False]
        results = merge_sort(vals)
        for i, (val, result) in enumerate(zip(vals, results)):
            with self.subTest(index=i):
                self.assertIs(result, val)


if __name__ == '__main__':
    unittest.main()
