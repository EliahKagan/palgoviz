#!/usr/bin/env python

"""Tests for the enumerations in enumerations.py."""

from numbers import Number
import unittest

from enumerations import BearBowl


class TestBearBowl(unittest.TestCase):
    """
    Tests for the BearBowl class.

    TODO: I have separated most test methods below into groups, each described
    by a comment. This suggests that the groups should be written as individual
    methods, with parameterization. Decide whether to do this and, if so, how.
    """

    # The three bowls really are bowls:

    def test_too_cold_is_a_bowl(self):
        self.assertIsInstance(BearBowl.TOO_COLD, BearBowl)

    def test_just_right_is_a_bowl(self):
        self.assertIsInstance(BearBowl.JUST_RIGHT, BearBowl)

    def test_too_hot_is_a_bowl(self):
        self.assertIsInstance(BearBowl.TOO_HOT, BearBowl)

    # They are not numbers:

    def test_too_cold_is_not_a_number(self):
        self.assertNotIsInstance(BearBowl.TOO_COLD, Number)

    def test_just_right_is_not_a_number(self):
        self.assertNotIsInstance(BearBowl.JUST_RIGHT, Number)

    def test_too_hot_is_not_a_number(self):
        self.assertNotIsInstance(BearBowl.TOO_HOT, Number)

    # Their reprs are code that evaluates to them (if BearBowl is in scope):

    def test_too_cold_repr_shows_attribute_access_from_class(self):
        self.assertEqual(repr(BearBowl.TOO_COLD), 'BearBowl.TOO_COLD')

    def test_just_right_repr_shows_attribute_access_from_class(self):
        self.assertEqual(repr(BearBowl.JUST_RIGHT), 'BearBowl.JUST_RIGHT')

    def test_too_hot_repr_shows_attribute_access_from_class(self):
        self.assertEqual(repr(BearBowl.TOO_HOT), 'BearBowl.TOO_HOT')

    # Their strs are that same code that evaluates to them:

    def test_too_cold_str_shows_attribute_access_from_class(self):
        self.assertEqual(str(BearBowl.TOO_COLD), 'BearBowl.TOO_COLD')

    def test_just_right_str_shows_attribute_access_from_class(self):
        self.assertEqual(str(BearBowl.JUST_RIGHT), 'BearBowl.JUST_RIGHT')

    def test_too_hot_str_shows_attribute_access_from_class(self):
        self.assertEqual(str(BearBowl.TOO_HOT), 'BearBowl.TOO_HOT')

    # They know their names, accessible through the name attribute:

    def test_too_cold_name_attribute_is_too_cold(self):
        self.assertEqual(BearBowl.TOO_COLD.name, 'TOO_COLD')

    def test_just_right_name_attribute_is_just_right(self):
        self.assertEqual(BearBowl.JUST_RIGHT.name, 'JUST_RIGHT')

    def test_too_hot_name_attribute_is_too_hot(self):
        self.assertEqual(BearBowl.TOO_HOT.name, 'TOO_HOT')

    # They are, as one would expect, equal to themselves:

    def test_too_cold_equals_too_cold(self):
        self.assertEqual(BearBowl.TOO_COLD, BearBowl.TOO_COLD)

    def test_just_right_equals_just_right(self):
        self.assertEqual(BearBowl.JUST_RIGHT, BearBowl.JUST_RIGHT)

    def test_too_hot_equals_too_hot(self):
        self.assertEqual(BearBowl.TOO_HOT, BearBowl.TOO_HOT)

    # They (i.e., differently named bowls) are not equal to each other:

    def test_too_cold_not_equal_to_just_right(self):
        with self.subTest(lhs=BearBowl.TOO_COLD, rhs=BearBowl.JUST_RIGHT):
            self.assertNotEqual(BearBowl.TOO_COLD, BearBowl.JUST_RIGHT)
        with self.subTest(lhs=BearBowl.JUST_RIGHT, rhs=BearBowl.TOO_COLD):
            self.assertNotEqual(BearBowl.JUST_RIGHT, BearBowl.TOO_COLD)

    def test_too_cold_not_equal_to_too_hot(self):
        with self.subTest(lhs=BearBowl.TOO_COLD, rhs=BearBowl.TOO_HOT):
            self.assertNotEqual(BearBowl.TOO_COLD, BearBowl.TOO_HOT)
        with self.subTest(lhs=BearBowl.TOO_HOT, rhs=BearBowl.TOO_COLD):
            self.assertNotEqual(BearBowl.TOO_HOT, BearBowl.TOO_COLD)

    def test_just_right_not_equal_to_too_hot(self):
        with self.subTest(lhs=BearBowl.JUST_RIGHT, rhs=BearBowl.TOO_HOT):
            self.assertNotEqual(BearBowl.JUST_RIGHT, BearBowl.TOO_HOT)
        with self.subTest(lhs=BearBowl.TOO_HOT, rhs=BearBowl.JUST_RIGHT):
            self.assertNotEqual(BearBowl.TOO_HOT, BearBowl.JUST_RIGHT)

    # Cooler bowls compare less than warmer bowls:

    def test_too_cold_less_than_just_right(self):
        self.assertLess(BearBowl.TOO_COLD, BearBowl.JUST_RIGHT)

    def test_too_cold_less_than_too_hot(self):
        self.assertLess(BearBowl.TOO_COLD, BearBowl.TOO_HOT)

    def test_just_right_less_than_too_hot(self):
        self.assertLess(BearBowl.JUST_RIGHT, BearBowl.TOO_HOT)

    # Warmer bowls compare greater than cooler bowls:

    def test_just_right_greater_than_too_cold(self):
        self.assertGreater(BearBowl.JUST_RIGHT, BearBowl.TOO_COLD)

    def test_too_hot_greater_than_too_cold(self):
        self.assertGreater(BearBowl.TOO_HOT, BearBowl.TOO_COLD)

    def test_too_hot_greater_than_just_right(self):
        self.assertGreater(BearBowl.TOO_HOT, BearBowl.JUST_RIGHT)

    # Bowls compare less than or equal to bowls that are no warmer:

    def test_too_cold_less_than_or_equal_to_itself(self):
        self.assertLessEqual(BearBowl.TOO_COLD, BearBowl.TOO_COLD)

    def test_too_cold_less_than_or_equal_to_just_right(self):
        self.assertLessEqual(BearBowl.TOO_COLD, BearBowl.JUST_RIGHT)

    def test_too_cold_less_than_or_equal_to_too_hot(self):
        self.assertLessEqual(BearBowl.TOO_COLD, BearBowl.TOO_HOT)

    def test_just_right_less_than_or_equal_to_itself(self):
        self.assertLessEqual(BearBowl.JUST_RIGHT, BearBowl.JUST_RIGHT)

    def test_just_right_less_than_or_equal_to_too_hot(self):
        self.assertLessEqual(BearBowl.JUST_RIGHT, BearBowl.TOO_HOT)

    def test_too_hot_less_than_or_equal_to_itself(self):
        self.assertLessEqual(BearBowl.TOO_HOT, BearBowl.TOO_HOT)

    # Bowls compare greater than or equal to bowls that are no cooler:

    def test_too_cold_greater_than_or_equal_to_itself(self):
        self.assertGreaterEqual(BearBowl.TOO_COLD, BearBowl.TOO_COLD)

    def test_just_right_greater_than_or_equal_to_too_cold(self):
        self.assertGreaterEqual(BearBowl.JUST_RIGHT, BearBowl.TOO_COLD)

    def test_just_right_greater_than_or_equal_to_itself(self):
        self.assertGreaterEqual(BearBowl.JUST_RIGHT, BearBowl.JUST_RIGHT)

    def test_too_hot_greater_than_or_equal_to_too_cold(self):
        self.assertGreaterEqual(BearBowl.TOO_HOT, BearBowl.TOO_COLD)

    def test_too_hot_greater_than_or_equal_to_just_right(self):
        self.assertGreaterEqual(BearBowl.TOO_HOT, BearBowl.JUST_RIGHT)

    def test_too_hot_greater_than_or_equal_to_itself(self):
        self.assertGreaterEqual(BearBowl.TOO_HOT, BearBowl.TOO_HOT)


if __name__ == '__main__':
    unittest.main()
