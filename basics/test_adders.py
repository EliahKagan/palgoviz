#!/usr/bin/env python

"""Tests for the adders module."""

import unittest

from parameterized import parameterized, parameterized_class

import adders


class _MyStr(str):
    """Trivially derived string type for testing nonidentical equal strings."""

    __slots__ = ()


@parameterized_class(('name', 'implementation'), [
    (adders.make_adder.__name__, staticmethod(adders.make_adder)),
    (adders.Adder.__name__, adders.Adder),
])
class TestSharedAdderBehavior(unittest.TestCase):
    """Shared tests for the make_adder function and Adder class."""

    def test_adder_adds(self):
        adder = self.implementation(6)
        self.assertEqual(adder(2), 8)

    def test_adder_is_reusable(self):
        adder = self.implementation(7)
        with self.subTest(call=1):
            self.assertEqual(adder(4), 11)
        with self.subTest(call=2):
            self.assertEqual(adder(10), 17)

    def test_adder_owned_addend_is_left_addend(self):
        adder = self.implementation('foo')
        self.assertEqual(adder('bar'), 'foobar')


class TestAdderExtensions(unittest.TestCase):
    """Tests of extended functionality provided by Adder but not make_adder."""

    def test_repr_is_codelike(self):
        adder = adders.Adder(7)
        self.assertEqual(repr(adder), 'Adder(7)')

    def test_repr_uses_repr_of_addend(self):
        adder = adders.Adder('cat')
        self.assertEqual(repr(adder), "Adder('cat')")

    def test_adders_of_same_addend_are_equal(self):
        lhs = adders.Adder(7)
        rhs = adders.Adder(7)
        self.assertEqual(lhs, rhs)

    def test_adders_of_equal_addends_of_different_type_are_equal(self):
        lhs = adders.Adder(7)
        rhs = adders.Adder(7.0)

        with self.subTest(lhs_type=int, rhs_type=float):
            self.assertEqual(lhs, rhs)

        with self.subTest(lhs_type=float, rhs_type=int):
            self.assertEqual(rhs, lhs)

    def test_adders_of_unequal_addends_are_not_equal(self):
        lhs = adders.Adder(6)
        rhs = adders.Adder(7)
        self.assertNotEqual(lhs, rhs)

    @parameterized.expand([('int', 7, 7.0), ('str', 'dog', _MyStr('dog'))])
    def test_equal_adders_hash_the_same(self, _name, lhs_addend, rhs_addend):
        lhs = adders.Adder(lhs_addend)
        rhs = adders.Adder(rhs_addend)
        self.assertEqual(hash(lhs), hash(rhs))

    def test_adders_work_in_hash_based_containers(self):
        lhs = {adders.Adder(7), adders.Adder(7),
               adders.Adder(6), adders.Adder(7.0)}

        rhs = {adders.Adder(6), adders.Adder(7)}

        self.assertSetEqual(lhs, rhs)

    def test_left_addend_attribute_holds_addend(self):
        adder = adders.Adder(7)
        self.assertEqual(adder.left_addend, 7)

    def test_left_addend_attribute_is_read_only(self):
        adder = adders.Adder(7)
        with self.assertRaises(AttributeError):
            adder.left_addend = 8

    def test_no_right_addend_attribute(self):
        adder = adders.Adder(7)
        with self.assertRaises(AttributeError):
            adder.right_addend

    def test_new_attributes_cannot_be_created(self):
        adder = adders.Adder(7)
        with self.assertRaises(AttributeError):
            adder.right_addend = 5


if __name__ == '__main__':
    unittest.main()
