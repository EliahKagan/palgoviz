#!/usr/bin/env python

"""Tests for the functions in recursion.py."""

import unittest

from compare import OrderIndistinct
from recursion import merge_two_slow


class TestMergeTwoSlow(unittest.TestCase):
    """Tests for the merge_two_slow function."""

    def test_is_a_stable_merge(self):
        lhs = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3)]
        rhs = [OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        expected = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
                    OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        result = merge_two_slow(lhs, rhs)
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
