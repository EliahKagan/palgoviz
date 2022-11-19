#!/usr/bin/env python

"""
Tests to review the meaning of basic Python language constructs.

Unlike other unit tests in this codebase, these tests test the Python
implementation. This is not because the implementation needs further testing,
but because tests express knowledge about how a system works (or should work),
and they can be run to find out if the claims they make are accurate.
"""

import unittest

from parameterized import parameterized


def _make_list():
    """Create a new list of three elements, for testing."""
    return ['Athos', 'Porthos', 'Aramis']


def _make_iterator():
    """Generator function yielding three elements, for testing."""
    yield 'Athos'
    yield 'Porthos'
    yield 'Aramis'


class TestList(unittest.TestCase):
    """
    Tests centrally involving lists.

    These are not mainly tests of lists (or len) themselves, but of the meaning
    of syntax that produces collections of particular lengths/sizes.
    """

    # FIXME: Change each "..." to the correct expected length. Do not modify
    # anything else, besides removing this comment when done. Fill in all
    # values (each "...") before running any of the tests for the first time.
    # The first three values (2, 1, and 0) are deliberately already filled in.
    @parameterized.expand([
        ([42, 76], 2),
        ([42], 1),
        ([], 0),
        ([_make_list()], ...),
        ([_make_iterator()], ...),
        ([_make_list(), "D'Artagnan"], ...),
        ([_make_iterator(), "D'Artagnan"], ...),
        ([*_make_list()], ...),
        ([*_make_iterator()], ...),
        ([*_make_list(), "D'Artagnan"], ...),
        ([*_make_iterator(), "D'Artagnan"], ...),
    ])
    def test_len(self, instance, expected_len):
        """Lists from list displays ("list expressions") have correct len."""
        actual_len = len(instance)
        self.assertEqual(actual_len, expected_len)


if __name__ == '__main__':
    unittest.main()
