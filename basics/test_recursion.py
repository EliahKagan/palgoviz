#!/usr/bin/env python

"""Tests for the functions in recursion.py."""

import unittest

from compare import OrderIndistinct, WeakDiamond
from recursion import merge_two_slow


class TestMergeTwoSlow(unittest.TestCase):
    """Tests for the merge_two_slow function."""

    def test_left_first_interleaved_merges(self):
        lhs = [1, 3, 5]
        rhs = [2, 4, 6]
        expected = [1, 2, 3, 4, 5, 6]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_right_first_interleaved_merges(self):
        lhs = [2, 4, 6]
        rhs = [1, 3, 5]
        expected = [1, 2, 3, 4, 5, 6]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_empty_list_on_left_gives_right_side(self):
        lhs = []
        rhs = [2, 4, 6]
        expected = [2, 4, 6]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_empty_tuple_on_left_gives_right_side(self):
        lhs = ()
        rhs = [2, 4, 6]
        expected = [2, 4, 6]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_empty_tuple_with_empty_list_gives_empty_list(self):
        lhs = ()
        rhs = []
        expected = []
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_empty_list_with_empty_tuple_gives_empty_list(self):
        lhs = []
        rhs = ()
        expected = []
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_empty_tuple_on_left_gives_right_side_as_list(self):
        """
        Merging an empty tuple with a tuple with duplicate leading items works.
        """
        lhs = ()
        rhs = (1, 1, 4, 7, 8)
        expected = [1, 1, 4, 7, 8]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_empty_tuple_on_right_gives_left_side_as_list(self):
        """
        Merging a tuple with duplicate leading items with an empty tuple works.
        """
        lhs = (1, 1, 4, 7, 8)
        rhs = ()
        expected = [1, 1, 4, 7, 8]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_is_a_stable_merge_when_items_do_not_compare(self):
        lhs = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3)]
        rhs = [OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        expected = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
                    OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_is_a_stable_merge_when_items_compare_equal(self):
        lhs = 1
        rhs = 1.0
        r1, r2 = merge_two_slow((lhs,), (rhs,))
        with self.subTest(result='r1'):
            self.assertIs(r1, lhs)
        with self.subTest(result='r2'):
            self.assertIs(r2, rhs)

    def test_is_a_stable_merge_when_some_items_compare_equal(self):
        lhs = [WeakDiamond.SOUTH, WeakDiamond.EAST, WeakDiamond.NORTH]
        rhs = [WeakDiamond.WEST, WeakDiamond.WEST]
        expected = [WeakDiamond.SOUTH, WeakDiamond.EAST, WeakDiamond.WEST,
                    WeakDiamond.WEST, WeakDiamond.NORTH]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
