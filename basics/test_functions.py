#!/usr/bin/env python

"""Tests for the functions in functions.py."""

import unittest

from parameterized import parameterized_class

import functions


@parameterized_class(('implementation_name',), [
    ('make_counter',),
    ('make_counter_alt',),
])
class TestMakeCounter(unittest.TestCase):
    """Tests for the make_counter and make_counter_alt functions."""

    __slots__ = ()

    def test_starts_at_zero_with_no_start_argument(self):
        f = self._implementation()
        self.assertEqual(f(), 0)

    def test_starts_at_start_argument_value_if_passed(self):
        f = self._implementation(76)
        self.assertEqual(f(), 76)

    def test_interleaved_counters_count_independently(self):
        f = self._implementation()
        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)

        g = self._implementation()
        self.assertEqual(f(), 2)
        self.assertEqual(g(), 0)
        self.assertEqual(f(), 3)
        self.assertEqual(g(), 1)
        self.assertEqual(g(), 2)

        h = self._implementation(10)
        self.assertEqual(h(), 10)
        self.assertEqual(f(), 4)
        self.assertEqual(g(), 3)
        self.assertEqual(h(), 11)
        self.assertEqual(g(), 4)
        self.assertEqual(h(), 12)
        self.assertEqual(h(), 13)
        self.assertEqual(g(), 5)
        self.assertEqual(g(), 6)
        self.assertEqual(f(), 5)
        self.assertEqual(h(), 14)

    @property
    def _implementation(self):
        """The function being tested."""
        return getattr(functions, self.implementation_name)


if __name__ == '__main__':
    unittest.main()
