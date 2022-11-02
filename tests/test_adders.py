#!/usr/bin/env python

"""Tests for the adders module."""

from abc import ABC, abstractmethod
import unittest

import attrs
from parameterized import parameterized

from algoviz import adders


class _TestAddersAbstract(ABC, unittest.TestCase):
    """ABC for unittest test classes for all adders."""

    @property
    @abstractmethod
    def impl(self):
        """The adder being tested."""
        raise NotImplementedError

    def test_adders_are_reusable(self):
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


class _TestAdderClassesAbstract(_TestAddersAbstract):
    """ABC for unittest test classes for adders implemented as classes."""

    @abstractmethod
    def test_repr(self):
        """
        Override this to test for a class-specific correct repr.

        This is abstract to avoid reproducing the logic of the code under test.
        """
        raise NotImplementedError

    @parameterized.expand([
        ('int_int', 2, 2),
        ('int_float', 2, 2.0),
        ('float_int', 3.0, 3),
        ('str_str', 'cat', 'cat'),
        ('bool_int_truthy', True, 1),
        ('int_bool_truthy', 1, True),
        ('bool_int_falsy', False, 0),
        ('int_bool_falsy', 0, False),
    ])
    def test_equal_if_addends_equal(self, _name, lhs_arg, rhs_arg):
        lhs = self.impl(lhs_arg)
        rhs = self.impl(rhs_arg)
        self.assertEqual(lhs, rhs)

    @parameterized.expand([
        ('int_int', 2, 3),
        ('int_float', 2, 4.0),
        ('float_int', 3.0, 5),
        ('str_str', 'cat', 'dog'),
        ('bool_int', True, 0),
        ('int_bool', 1, False),
    ])
    def test_not_equal_if_addends_not_equal(self, _name, lhs_arg, rhs_arg):
        lhs = self.impl(lhs_arg)
        rhs = self.impl(rhs_arg)
        self.assertNotEqual(lhs, rhs)

    @parameterized.expand([
        ('int_int', 2, 2),
        ('int_float', 2, 2.0),
        ('float_int', 3.0, 3),
        ('str_str', 'cat', 'cat'),
        ('bool_int_truthy', True, 1),
        ('bool_int_falsy', False, 0),
    ])
    def test_equal_adders_hash_equal(self, _name, lhs_arg, rhs_arg):
        lhs = self.impl(lhs_arg)
        rhs = self.impl(rhs_arg)
        self.assertEqual(hash(lhs), hash(rhs))

    def test_adders_work_in_hash_based_containers(self):
        lhs = {self.impl(7), self.impl(7), self.impl(6), self.impl(7.0)}
        rhs = {self.impl(6), self.impl(7)}
        self.assertEqual(lhs, rhs)

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


class TestMakeAdder(_TestAddersAbstract):
    """Tests for the make_adder function."""

    @property
    def impl(self):
        return adders.make_adder


class TestAdder(_TestAdderClassesAbstract):
    """Tests for the Adder class."""

    @property
    def impl(self):
        return adders.Adder

    def test_repr(self):
        """repr shows type and argument, and looks like Python code."""
        u = self.impl('cat')
        self.assertEqual(repr(u), "Adder('cat')")


class TestAdderA(_TestAdderClassesAbstract):
    """Tests for the AdderA class."""

    @property
    def impl(self):
        return adders.AdderA

    def test_repr(self):
        """
        repr shows type and argument, and looks like Python code.

        The argument is shown as a keyword argument, which the attrs-generated
        __repr__ implementation does. When this is unsuitable, __repr__ can be
        implemented manually, while still benefiting from the other features
        of attrs. (The same applies to @dataclasses.dataclass data classes.)
        In this case, this is not clearly worse than the positional version,
        because although there is only one argument, it makes sense to ensure
        the behavior in noncommutative "addition" is clearly communicated.
        """
        u = self.impl('cat')
        self.assertEqual(repr(u), "AdderA(left_addend='cat')")

    def test_class_is_attrs_class(self):
        self.assertTrue(attrs.has(self.impl))


del _TestAddersAbstract, _TestAdderClassesAbstract


if __name__ == '__main__':
    unittest.main()
