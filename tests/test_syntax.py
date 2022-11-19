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

    @parameterized.expand([
        ([42, 76], 2),
        ([42], 1),
        ([], 0),
        ([_make_list()], 1),
        ([_make_iterator()], 1),
        ([_make_list(), "D'Artagnan"], 2),
        ([_make_iterator(), "D'Artagnan"], 2),
        ([*_make_list()], 3),
        ([*_make_iterator()], 3),
        ([*_make_list(), "D'Artagnan"], 4),
        ([*_make_iterator(), "D'Artagnan"], 4),
    ])
    def test_len(self, instance, expected_len):
        """Lists from list displays ("list expressions") have correct len."""
        actual_len = len(instance)
        self.assertEqual(actual_len, expected_len)


if __name__ == '__main__':
    unittest.main()
