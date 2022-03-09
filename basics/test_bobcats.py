#!/usr/bin/env python

"""Tests for the bobcats module."""

import unittest

from bobcats import Bobcat


# TODO: Maybe deduplicate code by using setUp() to construct the countess.
class TestBobcat(unittest.TestCase):
    """Tests for the Bobcat class."""

    __slots__ = ()

    def test_bobcat_names_must_be_strings(self):
        with self.assertRaises(TypeError):
            Bobcat(0)

    def test_bobcat_names_must_be_nonempty(self):
        with self.assertRaises(ValueError):
            Bobcat('')

    def test_repr_is_well_formed(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        self.assertEqual(repr(bobcat), "Bobcat('Countess von Willdebrandt')")

    def test_repr_roundtrips_via_eval(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        copy = eval(repr(bobcat))
        self.assertEqual(bobcat, copy)

    def test_repr_is_well_formed_when_name_is_weird(self):
        weird_name = 'T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\'
        expected_repr = R"""Bobcat('T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\')"""
        bobcat = Bobcat(weird_name)
        self.assertEqual(repr(bobcat), expected_repr)

    def test_repr_roundtrips_via_eval_when_name_is_weird(self):
        bobcat = Bobcat('T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\')
        copy = eval(repr(bobcat))
        self.assertEqual(bobcat, copy)

    def test_str_good_to_announce_bobcat_at_fancy_parties(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        self.assertEqual(str(bobcat), 'Countess von Willdebrandt the bobcat')

    def test_str_good_to_announce_weird_named_bobcat_at_fancy_parties(self):
        weird_name = 'T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\'
        expected_str = 'T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\ the bobcat'
        bobcat = Bobcat(weird_name)
        self.assertEqual(str(bobcat), expected_str)

    def test_same_named_bobcats_are_the_same(self):
        first = Bobcat('Countess von Willdebrandt')
        second = Bobcat('Countess von Willdebrandt')
        self.assertEqual(first, second)

    def test_differently_named_bobcats_are_different(self):
        first = Bobcat('Countess von Willdebrandt')
        second = Bobcat('Countess von Willdebruvft')
        self.assertNotEqual(first, second)

    def test_no_bobcat_is_not_a_bobcat(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        non_bobcat = 'Countess von Willdebrandt'
        self.assertNotEqual(bobcat, non_bobcat)

    def test_no_non_bobcat_is_a_bobcat(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        non_bobcat = 'Countess von Willdebrandt'
        self.assertNotEqual(non_bobcat, bobcat)

    def test_same_named_bobcats_hash_the_same(self):
        first = Bobcat('Countess von Willdebrandt')
        second = Bobcat('Countess von Willdebrandt')
        self.assertEqual(hash(first), hash(second))

    def test_name_attribute_has_name(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        self.assertEqual(bobcat.name, 'Countess von Willdebrandt')

    def test_new_attributes_cannot_be_created(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        with self.assertRaises(AttributeError):
            bobcat.namr = 'Ekaterina'  # Misspelling of "name".

    def test_name_attribute_is_read_only(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        with self.assertRaises(AttributeError):
            bobcat.name = 'Ekaterina'

    def test_bobcats_seem_to_work_in_hash_based_containers(self):
        b1 = Bobcat('Countess von Willdebrandt')
        b2 = Bobcat('Countess von Willdebruvft')
        b3 = Bobcat('Countess von Willdebrandt')  # Same as b1.
        b4 = Bobcat('Bob')
        b5 = Bobcat('Ekaterina')
        b6 = Bobcat('T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\')
        b7 = Bobcat('Ekaterina') # Same as b5.
        b8 = Bobcat('Countess von Willdebrandt')  # Same as b1, again.

        d = dict.fromkeys([b1, b2, b3, b4, b5, b6, b7, b8])
        self.assertListEqual(list(d), [b1, b2, b4, b5, b6])


if __name__ == '__main__':
    unittest.main()
