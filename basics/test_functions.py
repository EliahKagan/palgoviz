#!/usr/bin/env python

"""Tests for the functions in functions.py."""

import abc
import unittest

import functions


class _TestMakeCounterBase(abc.ABC, unittest.TestCase):
    """Shared tests for the make_counter and make_counter_alt functions."""

    __slots__ = ()

    @property
    @abc.abstractmethod
    def implementation(self):
        """The make_counter implementation that this class tests."""
        ...

    def test_starts_at_zero_with_no_start_argument(self):
        f = self.implementation()
        self.assertEqual(f(), 0)

    def test_starts_at_start_argument_value_if_passed(self):
        f = self.implementation(76)
        self.assertEqual(f(), 76)

    def test_interleaved_counters_count_independently(self):
        f = self.implementation()
        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)

        g = self.implementation()
        self.assertEqual(f(), 2)
        self.assertEqual(g(), 0)
        self.assertEqual(f(), 3)
        self.assertEqual(g(), 1)
        self.assertEqual(g(), 2)

        h = self.implementation(10)
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


class TestMakeCounter(_TestMakeCounterBase):
    """Tests for the make_counter function."""

    __slots__ = ()

    @property
    def implementation(self):
        return functions.make_counter


class TestMakeCounterAlt(_TestMakeCounterBase):
    """Tests for the make_counter_alt function."""

    __slots__ = ()

    @property
    def implementation(self):
        return functions.make_counter_alt


del _TestMakeCounterBase


if __name__ == '__main__':
    unittest.main()
