#!/usr/bin/env python

"""Tests for functions in gencomp2.py."""

import itertools
import unittest

from parameterized import parameterized_class

import gencomp2


def implementations_to_test(*functions):
    """Decorator factory to parameterize a class to test multiple functions."""
    return parameterized_class(('impl',),
                               [(staticmethod(func),) for func in functions])


@implementations_to_test(
    itertools.product,
    gencomp2.product_two,
    gencomp2.product_two_alt,
)
class ProductTwoTests(unittest.TestCase):
    """Tests for product_two and product_two_alt."""

    __slots__ = ()

    def test_small_nontrivial_product_of_strings(self):
        result = self.impl('hi', 'bye')

        self.assertListEqual(
            list(result),
            [('h', 'b'), ('h', 'y'), ('h', 'e'),
             ('i', 'b'), ('i', 'y'), ('i', 'e')])


if __name__ == '__main__':
    unittest.main()
