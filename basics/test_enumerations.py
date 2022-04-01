#!/usr/bin/env python

"""Tests for the enumerations in enumerations.py."""

from numbers import Number
import unittest

from parameterized import parameterized

from enumerations import BearBowl


class TestBearBowl(unittest.TestCase):
    """
    Tests for the BearBowl class.

    TODO: I have separated most test methods below into groups, each described
    by a comment. This suggests that the groups should be written as individual
    methods, with parameterization. Decide whether to do this and, if so, how.
    """

    # The three bowls really are bowls:

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_is_a_bowl(self, name):
        bowl = getattr(BearBowl, name)
        self.assertIsInstance(bowl, BearBowl)

    # They are not numbers:

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_is_not_a_number(self, name):
        bowl = getattr(BearBowl, name)
        self.assertNotIsInstance(bowl, Number)

    # Their reprs are code that evaluates to them (if BearBowl is in scope):

    @parameterized.expand([
        ('TOO_COLD', 'BearBowl.TOO_COLD'),
        ('JUST_RIGHT', 'BearBowl.JUST_RIGHT'),
        ('TOO_HOT', 'BearBowl.TOO_HOT'),
    ])
    def test_bowl_repr_shows_attribute_access_from_class(self, name, expected):
        bowl = getattr(BearBowl, name)
        self.assertEqual(repr(bowl), expected)

    # Their strs are that same code that evaluates to them:

    @parameterized.expand([
        ('TOO_COLD', 'BearBowl.TOO_COLD'),
        ('JUST_RIGHT', 'BearBowl.JUST_RIGHT'),
        ('TOO_HOT', 'BearBowl.TOO_HOT'),
    ])
    def test_bowl_str_shows_attribute_access_from_class(self, name, expected):
        bowl = getattr(BearBowl, name)
        self.assertEqual(str(bowl), expected)

    # They know their names, accessible through the name attribute:

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_name_attribute_is_too_cold(self, name):
        bowl = getattr(BearBowl, name)
        self.assertEqual(bowl.name, name)

    # They are, as one would expect, equal to themselves:

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_equals_itself(self, name):
        lhs = getattr(BearBowl, name)
        rhs = getattr(BearBowl, name)
        self.assertEqual(lhs, rhs)

    # They (i.e., differently named bowls) are not equal to each other:

    @parameterized.expand([
        ('TC_JR', 'TOO_COLD', 'JUST_RIGHT'),
        ('JR_TC', 'JUST_RIGHT', 'TOO_COLD'),
        ('TC_TH', 'TOO_COLD', 'TOO_HOT'),
        ('TH_TC', 'TOO_HOT', 'TOO_COLD'),
        ('JR_TH', 'JUST_RIGHT', 'TOO_HOT'),
        ('TH_JR', 'TOO_HOT', 'JUST_RIGHT'),
    ])
    def test_differently_named_bowls_are_not_equal(self, _label,
                                                   lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertNotEqual(lhs, rhs)

    # Cooler bowls compare less than warmer bowls:

    @parameterized.expand([
        ('TC_JR', 'TOO_COLD', 'JUST_RIGHT'),
        ('TC_TH', 'TOO_COLD', 'TOO_HOT'),
        ('JR_TH', 'JUST_RIGHT', 'TOO_HOT'),
    ])
    def test_cooler_bowls_less_than_warmer_bowls(self, _label,
                                                 lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertLess(lhs, rhs)

    # Warmer bowls compare greater than cooler bowls:

    @parameterized.expand([
        ('JR_TC', 'JUST_RIGHT', 'TOO_COLD'),
        ('TH_TC', 'TOO_HOT', 'TOO_COLD'),
        ('TH_JR', 'TOO_HOT', 'JUST_RIGHT'),
    ])
    def test_warmer_bowls_greater_than_cooler_bowls(self, _label,
                                                    lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertGreater(lhs, rhs)

    # Bowls compare less than or equal to bowls that are no warmer:

    @parameterized.expand([
        ('TC_TC', 'TOO_COLD', 'TOO_COLD'),
        ('TC_JR', 'TOO_COLD', 'JUST_RIGHT'),
        ('TC_TH', 'TOO_COLD', 'TOO_HOT'),
        ('JR_JR', 'JUST_RIGHT', 'JUST_RIGHT'),
        ('JR_TH', 'JUST_RIGHT', 'TOO_HOT'),
        ('TH_TH', 'TOO_HOT', 'TOO_HOT'),
    ])
    def test_bowls_less_equal_to_warmer_bowls(self, _label,
                                              lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertLessEqual(lhs, rhs)

    # Bowls compare greater than or equal to bowls that are no cooler:

    @parameterized.expand([
        ('TC_TC', 'TOO_COLD', 'TOO_COLD'),
        ('JR_TC', 'JUST_RIGHT', 'TOO_COLD'),
        ('JR_JR', 'JUST_RIGHT', 'JUST_RIGHT'),
        ('TH_TC', 'TOO_HOT', 'TOO_COLD'),
        ('TH_JR', 'TOO_HOT', 'JUST_RIGHT'),
        ('TH_TH', 'TOO_HOT', 'TOO_HOT'),
    ])
    def test_bowls_greater_equal_to_cooler_bowls(self, _label,
                                                 lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertGreaterEqual(lhs, rhs)


if __name__ == '__main__':
    unittest.main()
