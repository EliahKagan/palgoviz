#!/usr/bin/env python

"""Tests for the enumerations in enumerations.py."""

from numbers import Number
import unittest

from parameterized import parameterized

from enumerations import BearBowl, Guests


class TestBearBowl(unittest.TestCase):
    """Tests for the BearBowl class."""

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_is_a_bowl(self, name):
        bowl = getattr(BearBowl, name)
        self.assertIsInstance(bowl, BearBowl)

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_is_not_a_number(self, name):
        bowl = getattr(BearBowl, name)
        self.assertNotIsInstance(bowl, Number)

    @parameterized.expand([
        ('TOO_COLD', 'BearBowl.TOO_COLD'),
        ('JUST_RIGHT', 'BearBowl.JUST_RIGHT'),
        ('TOO_HOT', 'BearBowl.TOO_HOT'),
    ])
    def test_bowl_repr_shows_attribute_access_from_class(self, name, expected):
        bowl = getattr(BearBowl, name)
        self.assertEqual(repr(bowl), expected)

    @parameterized.expand([
        ('TOO_COLD', 'BearBowl.TOO_COLD'),
        ('JUST_RIGHT', 'BearBowl.JUST_RIGHT'),
        ('TOO_HOT', 'BearBowl.TOO_HOT'),
    ])
    def test_bowl_str_shows_attribute_access_from_class(self, name, expected):
        bowl = getattr(BearBowl, name)
        self.assertEqual(str(bowl), expected)

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_name_attribute_is_too_cold(self, name):
        bowl = getattr(BearBowl, name)
        self.assertEqual(bowl.name, name)

    @parameterized.expand(['TOO_COLD', 'JUST_RIGHT', 'TOO_HOT'])
    def test_bowl_equals_itself(self, name):
        lhs = getattr(BearBowl, name)
        rhs = getattr(BearBowl, name)
        self.assertEqual(lhs, rhs)

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

    @parameterized.expand([
        ('TC_TC', 'TOO_COLD', 'TOO_COLD'),
        ('TC_JR', 'TOO_COLD', 'JUST_RIGHT'),
        ('TC_TH', 'TOO_COLD', 'TOO_HOT'),
        ('JR_JR', 'JUST_RIGHT', 'JUST_RIGHT'),
        ('JR_TH', 'JUST_RIGHT', 'TOO_HOT'),
        ('TH_TH', 'TOO_HOT', 'TOO_HOT'),
    ])
    def test_bowls_less_equal_to_not_cooler_bowls(self, _label,
                                                  lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertLessEqual(lhs, rhs)

    @parameterized.expand([
        ('TC_TC', 'TOO_COLD', 'TOO_COLD'),
        ('JR_TC', 'JUST_RIGHT', 'TOO_COLD'),
        ('JR_JR', 'JUST_RIGHT', 'JUST_RIGHT'),
        ('TH_TC', 'TOO_HOT', 'TOO_COLD'),
        ('TH_JR', 'TOO_HOT', 'JUST_RIGHT'),
        ('TH_TH', 'TOO_HOT', 'TOO_HOT'),
    ])
    def test_bowls_greater_equal_to_not_warmer_bowls(self, _label,
                                                     lhs_name, rhs_name):
        lhs = getattr(BearBowl, lhs_name)
        rhs = getattr(BearBowl, rhs_name)
        self.assertGreaterEqual(lhs, rhs)


class TestGuests(unittest.TestCase):
    """Tests for the Guests class."""

    def test_intersection_of_party_and_party2(self):
        """Only Alice and Frank attended both parties."""
        expected = Guests.ALICE | Guests.FRANK
        actual = Guests.PARTY & Guests.PARTY2
        self.assertIs(actual, expected)

    def test_union_of_party_and_party2(self):
        """Alice, Bob, Cassidy, Erin, and Frank attended some party."""
        expected = (Guests.ALICE | Guests.BOB | Guests.CASSIDY
                    | Guests.ERIN | Guests.FRANK)
        actual = Guests.PARTY | Guests.PARTY2
        self.assertIs(actual, expected)

    def test_complement_of_party(self):
        """Bob, Derek, Erin, Gerald, and Heather did not attended party."""
        expected = (Guests.BOB | Guests.DEREK | Guests.ERIN
                    | Guests.GERALD | Guests.HEATHER)
        actual = ~Guests.PARTY
        self.assertIs(actual, expected)

    def test_difference_party_party2(self):
        """Cassidy attended party and did not attend party2."""
        expected = Guests.CASSIDY
        actual = Guests.PARTY & ~Guests.PARTY2
        self.assertIs(actual, expected)

    def test_difference_party_party2_with_minus_operator(self):
        """Cassidy attended party and did not attend party2 and - operator works."""
        expected = Guests.CASSIDY
        actual = Guests.PARTY - Guests.PARTY2
        self.assertIs(actual, expected)

    def test_difference_party2_party(self):
        """Bob and Erin attended party2 and did not attend party."""
        expected = Guests.BOB | Guests.ERIN
        actual = Guests.PARTY2 & ~Guests.PARTY
        self.assertIs(actual, expected)

    def test_symmetric_difference_party_party2(self):
        """Bob, Cassidy, and Erin attended only one party."""
        expected = Guests.BOB | Guests.CASSIDY | Guests.ERIN
        actual = Guests.PARTY ^ Guests.PARTY2
        self.assertIs(actual, expected)

    def test_symmetric_difference_is_symmetric(self):
        """Symmetric difference shouldn't change based on order."""
        lhs = Guests.PARTY ^ Guests.PARTY2
        rhs = Guests.PARTY2 ^ Guests.PARTY
        self.assertIs(lhs, rhs)

    # Test for <

    def test_alice_trial_proper_subset_frank_trial(self):
        self.assertTrue(Guests.ALICE_TRIAL < Guests.FRANK_TRIAL)

    def test_alice_trial_not_proper_subset_alice_trial(self):
        self.assertFalse(Guests.ALICE_TRIAL < Guests.ALICE_TRIAL)

    def test_frank_trial_not_proper_subset_alice_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL < Guests.ALICE_TRIAL)

    def test_bob_trial_not_proper_subset_erin_trial(self):
        self.assertFalse(Guests.BOB_TRIAL < Guests.ERIN_TRIAL)

    def test_frank_trial_not_proper_subset_erin_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL < Guests.ERIN_TRIAL)

    # Tests for <=

    def test_alice_trial_subset_frank_trial(self):
        self.assertTrue(Guests.ALICE_TRIAL <= Guests.FRANK_TRIAL)

    def test_alice_trial_subset_alice_trial(self):
        self.assertTrue(Guests.ALICE_TRIAL <= Guests.ALICE_TRIAL)

    def test_frank_trial_not_subset_alice_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL <= Guests.ALICE_TRIAL)

    def test_bob_trial_not_subset_erin_trial(self):
        self.assertFalse(Guests.BOB_TRIAL <= Guests.ERIN_TRIAL)

    def test_frank_trial_not_subset_erin_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL <= Guests.ERIN_TRIAL)

    # Tests for >

    def test_frank_trial_proper_superset_alice_trial(self):
        self.assertTrue(Guests.FRANK_TRIAL > Guests.ALICE_TRIAL)

    def test_frank_trial_not_proper_superset_frank_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL > Guests.FRANK_TRIAL)

    def test_alice_trial_not_proper_superset_frank_trial(self):
        self.assertFalse(Guests.ALICE_TRIAL > Guests.FRANK_TRIAL)

    def test_bob_trial_not_proper_superset_erin_trial(self):
        self.assertFalse(Guests.BOB_TRIAL > Guests.ERIN_TRIAL)

    def test_frank_trial_not_proper_superset_erin_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL > Guests.ERIN_TRIAL)

    # Tests for >=

    def test_frank_trial_superset_alice_trial(self):
        self.assertTrue(Guests.FRANK_TRIAL >= Guests.ALICE_TRIAL)

    def test_frank_trial_superset_frank_trial(self):
        self.assertTrue(Guests.FRANK_TRIAL >= Guests.FRANK_TRIAL)

    def test_alice_trial_not_superset_frank_trial(self):
        self.assertFalse(Guests.ALICE_TRIAL >= Guests.FRANK_TRIAL)

    def test_bob_trial_not_superset_erin_trial(self):
        self.assertFalse(Guests.BOB_TRIAL >= Guests.ERIN_TRIAL)

    def test_frank_trial_not_superset_erin_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL >= Guests.ERIN_TRIAL)

    # Other tests

    def test_nobody_attended_cassidy_trial(self):
        for guest in (Guests.ALICE,
                      Guests.BOB,
                      Guests.CASSIDY,
                      Guests.DEREK,
                      Guests.ERIN,
                      Guests.FRANK,
                      Guests.GERALD,
                      Guests.HEATHER):
            with self.subTest(guest=guest):
                self.assertFalse(guest & Guests.CASSIDY_TRIAL)

    def test_cassidy_trial_empty(self):
        self.assertFalse(Guests.CASSIDY_TRIAL)

    def test_alice_trial_nonempty(self):
        self.assertTrue(Guests.ALICE_TRIAL)

    def test_zero_attended_cassidy_trial(self):
        self.assertEqual(len(Guests.CASSIDY_TRIAL), 0)

    def test_three_attended_erin_trial(self):
        self.assertEqual(len(Guests.ERIN_TRIAL), 3)

    @parameterized.expand([
         ('A', Guests.A, Guests.ALICE),
         ('B', Guests.B, Guests.BOB),
         ('C', Guests.C, Guests.CASSIDY),
         ('D', Guests.D, Guests.DEREK),
         ('E', Guests.E, Guests.ERIN),
         ('F', Guests.F, Guests.FRANK),
         ('G', Guests.G, Guests.GERALD),
         ('H', Guests.H, Guests.HEATHER),
    ])
    def test_guest_short_is_long(self, _name, short, long):
        self.assertIs(short, long)

    @parameterized.expand([
         ('A', Guests.A, 'ALICE'),
         ('B', Guests.B, 'BOB'),
         ('C', Guests.C, 'CASSIDY'),
         ('D', Guests.D, 'DEREK'),
         ('E', Guests.E, 'ERIN'),
         ('F', Guests.F, 'FRANK'),
         ('G', Guests.G, 'GERALD'),
         ('H', Guests.H, 'HEATHER'),
    ])
    def test_short_has_correct_name_attribute(self, _name, short, expected):
        self.assertEqual(short.name, expected)

    def test_bob_trial_is_disjoint_erin_trial(self):
        self.assertTrue(Guests.BOB_TRIAL.isdisjoint(Guests.ERIN_TRIAL))

    def test_frank_trial_is_not_disjoint_erin_trial(self):
        self.assertFalse(Guests.FRANK_TRIAL.isdisjoint(Guests.ERIN_TRIAL))

if __name__ == '__main__':
    unittest.main()
