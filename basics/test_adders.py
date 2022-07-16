#!/usr/bin/env python

"""Tests for the adders module."""

from abc import ABC, abstractmethod
import unittest

from parameterized import parameterized

from adders import Adder, make_adder


class _TestAddersAbstract(ABC, unittest.TestCase):
    """ABC for for tests for adders."""
    @property
    @abstractmethod
    def impl(self):
        """The adder being tested."""

    def test_adders_are_resuable(self):
        f = self.impl(7)

        with self.subTest(arg=4):
            self.assertEqual(f(4), 11)

        with self.subTest(arg=10):
            self.assertEqual(f(10), 17)

    def test_adds(self):
        self.assertEqual(self.impl(6)(2), 8)

    def test_adds_in_order(self):
        s = self.impl('cat')
        self.assertEqual(s(' dog'), 'cat dog')


class TestMakeAdder(_TestAddersAbstract):
    """Tests for the make_adder function."""

    @property
    def impl(self):
        return make_adder


class TestAdder(_TestAddersAbstract):
    """Tests for the Adder class."""

    @property
    def impl(self):
        return Adder

    def test_repr_shows_type_and_arg_and_looks_like_python_code(self):
        u = self.impl('cat')
        self.assertEqual(repr(u), "Adder('cat')")

    @parameterized.expand([  # FIXME: Consider using type-based _name values.
        ('2_2', 2, 2),
        ('2_2.0', 2, 2.0),
        ('cat', 'cat', 'cat'),
        ('True_1', True, 1),
        ('False_0', False, 0),
    ])
    def test_equal_if_addends_equal(self, _name, lhs_arg, rhs_arg):
        lhs = self.impl(lhs_arg)
        rhs = self.impl(rhs_arg)
        self.assertEqual(lhs, rhs)

    # FIXME: Add a test of the basic import properties for hash.

    def test_equality_and_hashability(self):
        lhs = {self.impl(7), self.impl(7), self.impl(6), self.impl(7.0)}
        rhs = {self.impl(6), self.impl(7)}
        self.assertTrue(lhs == rhs)  # FIXME: Use assertEqual here.

    def test_can_access_left_addend(self):
        a = self.impl(7)
        self.assertEqual(a.left_addend, 7)

    def test_cannot_assign_left_addend(self):
        a = self.impl(7)
        with self.assertRaises(AttributeError):
            a.left_addend = 8

    def test_cannot_assign_new_attributes(self):
        a = self.impl(7)
        with self.assertRaises(AttributeError):
            a.right_addend = 5


del _TestAddersAbstract


if __name__ == '__main__':
    unittest.main()
