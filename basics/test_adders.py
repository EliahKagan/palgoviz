#!/usr/bin/env python

"""Tests for the adders module."""

import unittest

from adders import Adder, make_adder


class TestMakeAdder(unittest.TestCase):
    """Tests for the make_adder function."""

    def test_adders_are_resuable(self):
        f = make_adder(7)

        with self.subTest(arg=4):
            self.assertEqual(f(4), 11)

        with self.subTest(arg=10):
            self.assertEqual(f(10), 17)

    def test_adds(self):
        self.assertEqual(make_adder(6)(2), 8)

    def test_adds_in_order(self):
        s = make_adder('cat')
        self.assertEqual(s(' dog'), 'cat dog')


class TestAdder(unittest.TestCase):
    """Tests for the Adder class."""

    def test_adders_are_resusable(self):
        a = Adder(7)

        with self.subTest(arg=4):
            self.assertEqual(a(4), 11)

        with self.subTest(arg=10):
            self.assertEqual(a(10), 17)

    def test_adds(self):
        self.assertEqual(Adder(6)(2), 8)

    def test_adds_in_order(self):
        u = Adder('cat')
        self.assertEqual(u(' dog'), 'cat dog')

    def test_repr_shows_type_and_arg_and_looks_like_python_code(self):
        u = Adder('cat')
        self.assertEqual(repr(u), "Adder('cat')")

    def test_equality_and_hashability(self):
        lhs = {Adder(7), Adder(7), Adder(6), Adder(7.0)}
        rhs = {Adder(6), Adder(7)}
        self.assertTrue(lhs == rhs)

    def test_can_access_left_addend(self):
        a = Adder(7)
        self.assertEqual(a.left_addend, 7)

    def test_cannot_assign_left_addend(self):
        a = Adder(7)
        with self.assertRaises(AttributeError):
            a.left_addend = 8

    def test_cannot_assign_new_attributes(self):
        a = Adder(7)
        with self.assertRaises(AttributeError):
            a.right_addend = 5


if __name__ == '__main__':
    unittest.main()
