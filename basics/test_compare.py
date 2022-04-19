#!/usr/bin/env python

"""
Tests for the types in compare.py.

TODO: It may be interesting to compare these tests' style to the style in
test_bobcats.py (once that is merged).
"""

import copy
from fractions import Fraction
import pickle
import unittest

from parameterized import parameterized

from compare import OrderIndistinct, Patient, WeakDiamond


class TestWeakDiamond(unittest.TestCase):
    """Tests for the WeakDiamond class."""

    @parameterized.expand([
        ('NORTH, NORTH', 'NORTH', 'NORTH', True, False),
        ('NORTH, SOUTH', 'NORTH', 'SOUTH', False, True),
        ('NORTH, EAST', 'NORTH', 'EAST', False, True),
        ('NORTH, WEST', 'NORTH', 'WEST', False, True),
        ('SOUTH, NORTH', 'SOUTH', 'NORTH', False, True),
        ('SOUTH, SOUTH', 'SOUTH', 'SOUTH', True, False),
        ('SOUTH, EAST', 'SOUTH', 'EAST', False, True),
        ('SOUTH, WEST', 'SOUTH', 'WEST', False, True),
        ('EAST, NORTH', 'EAST', 'NORTH', False, True),
        ('EAST, SOUTH', 'EAST', 'SOUTH', False, True),
        ('EAST, EAST', 'EAST', 'EAST', True, False),
        ('EAST, WEST', 'EAST', 'WEST', False, True),
        ('WEST, NORTH', 'WEST', 'NORTH', False, True),
        ('WEST, SOUTH', 'WEST', 'SOUTH', False, True),
        ('WEST, EAST', 'WEST', 'EAST', False, True),
        ('WEST, WEST', 'WEST', 'WEST', True, False),
    ])
    def test_equal(self, _label, lhs_name, rhs_name, expected_eq, expected_ne):
        """Enumerators are equal (only) when they are the same direction."""
        lhs = getattr(WeakDiamond, lhs_name)
        rhs = getattr(WeakDiamond, rhs_name)
        with self.subTest(op='=='):
            actual = lhs == rhs
            self.assertIs(actual, expected_eq)
        with self.subTest(op='!='):
            actual = lhs != rhs
            self.assertIs(actual, expected_ne)

    @parameterized.expand([
        ('NORTH, NORTH', 'NORTH', 'NORTH', False),
        ('NORTH, SOUTH', 'NORTH', 'SOUTH', False),
        ('NORTH, EAST', 'NORTH', 'EAST', False),
        ('NORTH, WEST', 'NORTH', 'WEST', False),
        ('SOUTH, NORTH', 'SOUTH', 'NORTH', True),
        ('SOUTH, SOUTH', 'SOUTH', 'SOUTH', False),
        ('SOUTH, EAST', 'SOUTH', 'EAST', True),
        ('SOUTH, WEST', 'SOUTH', 'WEST', True),
        ('EAST, NORTH', 'EAST', 'NORTH', True),
        ('EAST, SOUTH', 'EAST', 'SOUTH', False),
        ('EAST, EAST', 'EAST', 'EAST', False),
        ('EAST, WEST', 'EAST', 'WEST', False),
        ('WEST, NORTH', 'WEST', 'NORTH', True),
        ('WEST, SOUTH', 'WEST', 'SOUTH', False),
        ('WEST, EAST', 'WEST', 'EAST', False),
        ('WEST, WEST', 'WEST', 'WEST', False),
    ])
    def test_less_than(self, _label, lhs_name, rhs_name, expected):
        """A direction is less (only) when it is more south."""
        lhs = getattr(WeakDiamond, lhs_name)
        rhs = getattr(WeakDiamond, rhs_name)
        actual = lhs < rhs
        self.assertIs(actual, expected)

    @parameterized.expand([
        ('NORTH, NORTH', 'NORTH', 'NORTH', False),
        ('NORTH, SOUTH', 'NORTH', 'SOUTH', True),
        ('NORTH, EAST', 'NORTH', 'EAST', True),
        ('NORTH, WEST', 'NORTH', 'WEST', True),
        ('SOUTH, NORTH', 'SOUTH', 'NORTH', False),
        ('SOUTH, SOUTH', 'SOUTH', 'SOUTH', False),
        ('SOUTH, EAST', 'SOUTH', 'EAST', False),
        ('SOUTH, WEST', 'SOUTH', 'WEST', False),
        ('EAST, NORTH', 'EAST', 'NORTH', False),
        ('EAST, SOUTH', 'EAST', 'SOUTH', True),
        ('EAST, EAST', 'EAST', 'EAST', False),
        ('EAST, WEST', 'EAST', 'WEST', False),
        ('WEST, NORTH', 'WEST', 'NORTH', False),
        ('WEST, SOUTH', 'WEST', 'SOUTH', True),
        ('WEST, EAST', 'WEST', 'EAST', False),
        ('WEST, WEST', 'WEST', 'WEST', False),
    ])
    def test_greater_than(self, _label, lhs_name, rhs_name, expected):
        """A direction is greater (only) when it is more north."""
        lhs = getattr(WeakDiamond, lhs_name)
        rhs = getattr(WeakDiamond, rhs_name)
        actual = lhs > rhs
        self.assertIs(actual, expected)

    @parameterized.expand([
        ('NORTH, NORTH', 'NORTH', 'NORTH', True),
        ('NORTH, SOUTH', 'NORTH', 'SOUTH', False),
        ('NORTH, EAST', 'NORTH', 'EAST', False),
        ('NORTH, WEST', 'NORTH', 'WEST', False),
        ('SOUTH, NORTH', 'SOUTH', 'NORTH', True),
        ('SOUTH, SOUTH', 'SOUTH', 'SOUTH', True),
        ('SOUTH, EAST', 'SOUTH', 'EAST', True),
        ('SOUTH, WEST', 'SOUTH', 'WEST', True),
        ('EAST, NORTH', 'EAST', 'NORTH', True),
        ('EAST, SOUTH', 'EAST', 'SOUTH', False),
        ('EAST, EAST', 'EAST', 'EAST', True),
        ('EAST, WEST', 'EAST', 'WEST', False),
        ('WEST, NORTH', 'WEST', 'NORTH', True),
        ('WEST, SOUTH', 'WEST', 'SOUTH', False),
        ('WEST, EAST', 'WEST', 'EAST', False),
        ('WEST, WEST', 'WEST', 'WEST', True),
    ])
    def test_less_equal(self, _label, lhs_name, rhs_name, expected):
        """A direction is "<=" (only) when it is less or it is equal."""
        lhs = getattr(WeakDiamond, lhs_name)
        rhs = getattr(WeakDiamond, rhs_name)
        actual = lhs <= rhs
        self.assertIs(actual, expected)

    @parameterized.expand([
        ('NORTH, NORTH', 'NORTH', 'NORTH', True),
        ('NORTH, SOUTH', 'NORTH', 'SOUTH', True),
        ('NORTH, EAST', 'NORTH', 'EAST', True),
        ('NORTH, WEST', 'NORTH', 'WEST', True),
        ('SOUTH, NORTH', 'SOUTH', 'NORTH', False),
        ('SOUTH, SOUTH', 'SOUTH', 'SOUTH', True),
        ('SOUTH, EAST', 'SOUTH', 'EAST', False),
        ('SOUTH, WEST', 'SOUTH', 'WEST', False),
        ('EAST, NORTH', 'EAST', 'NORTH', False),
        ('EAST, SOUTH', 'EAST', 'SOUTH', True),
        ('EAST, EAST', 'EAST', 'EAST', True),
        ('EAST, WEST', 'EAST', 'WEST', False),
        ('WEST, NORTH', 'WEST', 'NORTH', False),
        ('WEST, SOUTH', 'WEST', 'SOUTH', True),
        ('WEST, EAST', 'WEST', 'EAST', False),
        ('WEST, WEST', 'WEST', 'WEST', True),
    ])
    def test_greater_equal(self, _label, lhs_name, rhs_name, expected):
        """A direction is ">=" (only) when it is greater or it is equal."""
        lhs = getattr(WeakDiamond, lhs_name)
        rhs = getattr(WeakDiamond, rhs_name)
        actual = lhs >= rhs
        self.assertIs(actual, expected)


class TestPatient(unittest.TestCase):
    """Tests for the Patient class."""

    def test_initials_starts_as_construction_initials(self):
        patient = Patient('XY', 500)
        self.assertEqual(patient.initials, 'XY')

    def test_initials_change_when_assigned(self):
        patient = Patient('WZ', 600)
        patient.initials = 'UV'
        self.assertEqual(patient.initials, 'UV')

    def test_priority_starts_as_start_priority(self):
        patient = Patient('YX', 550)
        self.assertEqual(patient.priority, 550)

    def test_priority_can_be_increased(self):
        patient = Patient('ZW', 900)
        patient.priority += 50
        self.assertEqual(patient.priority, 950)

    def test_priority_can_be_decreased(self):
        patient = Patient('VU', 900)
        patient.priority -= 50
        self.assertEqual(patient.priority, 850)

    def test_mrn_is_int(self):
        patient = Patient('GP', 8080)
        self.assertIsInstance(patient.mrn, int)

    def test_mrn_different_with_same_initials_and_priority(self):
        p = Patient('AB', 1000)
        q = Patient('AB', 1000)
        self.assertNotEqual(p.mrn, q.mrn)

    def test_mrn_different_with_same_initials_different_priority(self):
        p = Patient('CD', 1010)
        q = Patient('CD', 1100)
        self.assertNotEqual(p.mrn, q.mrn)

    def test_mrn_different_with_different_initials_same_priority(self):
        p = Patient('EF', 2000)
        q = Patient('GH', 2000)
        self.assertNotEqual(p.mrn, q.mrn)

    def test_mrn_different_with_different_initials_and_priority(self):
        p = Patient('IJ', 2100)
        q = Patient('KL', 2010)
        self.assertNotEqual(p.mrn, q.mrn)

    def test_mrn_cannot_be_set(self):
        patient = Patient('MN', 3000)
        with self.assertRaises(AttributeError):
            patient.mrn = 1472

    def test_new_attributes_cannot_be_created(self):
        patient = Patient('OP', 2865)
        with self.assertRaises(AttributeError):
            patient.nonexistent_attribute = 76

    def test_repr_shows_mrn_initials_priority(self):
        patient = Patient('QF', 999)
        mrn = patient.mrn
        if not isinstance(mrn, int):
            raise Exception("mrn isn't an int, can't create expected repr")
        expected = f"<Patient mrn={patient.mrn} initials='QF' priority=999>"

        actual = repr(patient)
        self.assertEqual(actual, expected)

    def test_repr_reflects_changed_initials(self):
        patient = Patient('RG', 999)
        mrn = patient.mrn
        if not isinstance(mrn, int):
            raise Exception("mrn isn't an int, can't create expected repr")

        expected = f"<Patient mrn={patient.mrn} initials='GR' priority=999>"
        patient.initials = 'GR'

        actual = repr(patient)
        self.assertEqual(actual, expected)

    def test_repr_reflects_changed_priority(self):
        patient = Patient('SH', 999)
        mrn = patient.mrn
        if not isinstance(mrn, int):
            raise Exception("mrn isn't an int, can't create expected repr")

        expected = f"<Patient mrn={patient.mrn} initials='SH' priority=570>"
        patient.priority = 570

        actual = repr(patient)
        self.assertEqual(actual, expected)

    def test_equal_to_self(self):
        patient = Patient('AZ', 6871)
        self.assertEqual(patient, patient)

    def test_not_equal_to_other_with_same_initials_and_priority(self):
        lhs = Patient('BA', 1000)
        rhs = Patient('BA', 1000)
        self.assertNotEqual(lhs, rhs)

    def test_not_equal_to_other_with_same_initials_different_priority(self):
        lhs = Patient('DC', 1010)
        rhs = Patient('DC', 1100)
        self.assertNotEqual(lhs, rhs)

    def test_not_equal_to_other_with_different_initials_same_priority(self):
        lhs = Patient('FE', 2000)
        rhs = Patient('HG', 2000)
        self.assertNotEqual(lhs, rhs)

    def test_not_equal_to_other_with_different_initials_and_priority(self):
        lhs = Patient('JI', 2100)
        rhs = Patient('LK', 2010)
        self.assertNotEqual(lhs, rhs)

    def test_equal_to_shallow_copy(self):
        """Patient records are flat so even shallow copying works."""
        original = Patient('DW', 13187)
        duplicate = copy.copy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertEqual(original, duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertEqual(duplicate, original)

    def test_equal_to_deep_copy(self):
        """Deep copying works (though is overkill) for patient records."""
        original = Patient('EX', 12221)
        duplicate = copy.deepcopy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertEqual(original, duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertEqual(duplicate, original)

    def test_equal_to_pickling_clone(self):
        """Patient records can be serialized and deserialized by pickling."""
        original = Patient('FY', 11800)
        duplicate = pickle.loads(pickle.dumps(original))
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertEqual(original, duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertEqual(duplicate, original)

    def test_not_less_than_itself(self):
        patient = Patient('AM', 4041)
        self.assertFalse(patient < patient)

    def test_not_less_than_shallow_copy(self):
        original = Patient('BN', 3074)
        duplicate = copy.copy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertFalse(original < duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertFalse(duplicate < original)

    def test_not_less_than_deep_copy(self):
        original = Patient('CO', 1122)
        duplicate = copy.deepcopy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertFalse(original < duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertFalse(duplicate < original)

    def test_not_less_than_pickling_clone(self):
        original = Patient('DP', 7970)
        duplicate = pickle.loads(pickle.dumps(original))
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertFalse(original < duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertFalse(duplicate < original)

    @parameterized.expand([
        ('same initials', 'XX', 'XX', 1001, 1001),
        ('incr initials', 'XX', 'YY', 1001, 1001),
        ('decr initials', 'YY', 'XX', 1001, 1001),
    ])
    def test_not_less_than_other_same_priority_patient(
            self, _label,
            lhs_initials, rhs_initials, lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs < rhs)

    @parameterized.expand([
        ('same initials', 'WW', 'WW', 1000, 1002),
        ('incr initials', 'WW', 'ZZ', 1000, 1002),
        ('decr initials', 'ZZ', 'WW', 1000, 1002),
    ])
    def test_less_than_higher_priority_patient(self, _label,
                                               lhs_initials, rhs_initials,
                                               lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertTrue(lhs < rhs)

    @parameterized.expand([
        ('same initials', 'PP', 'PP', 1002, 1000),
        ('incr initials', 'PP', 'QQ', 1002, 1000),
        ('decr initials', 'QQ', 'PP', 1002, 1000),
    ])
    def test_not_less_than_lower_priority_patient(self, _label,
                                                  lhs_initials, rhs_initials,
                                                  lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs < rhs)

    def test_less_than_or_equal_to_itself(self):
        patient = Patient('AM', 4041)
        self.assertTrue(patient <= patient)

    def test_less_than_or_equal_to_shallow_copy(self):
        original = Patient('BN', 3074)
        duplicate = copy.copy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertTrue(original <= duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertTrue(duplicate <= original)

    def test_less_than_or_equal_to_deep_copy(self):
        original = Patient('CO', 1122)
        duplicate = copy.deepcopy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertTrue(original <= duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertTrue(duplicate <= original)

    def test_less_than_or_equal_to_pickling_clone(self):
        original = Patient('DP', 7970)
        duplicate = pickle.loads(pickle.dumps(original))
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertTrue(original <= duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertTrue(duplicate <= original)

    @parameterized.expand([
        ('same initials', 'XX', 'XX', 1001, 1001),
        ('incr initials', 'XX', 'YY', 1001, 1001),
        ('decr initials', 'YY', 'XX', 1001, 1001),
    ])
    def test_not_less_equal_other_same_priority_patient(
            self, _label,
            lhs_initials, rhs_initials, lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs <= rhs)

    @parameterized.expand([
        ('same initials', 'WW', 'WW', 1000, 1002),
        ('incr initials', 'WW', 'ZZ', 1000, 1002),
        ('decr initials', 'ZZ', 'WW', 1000, 1002),
    ])
    def test_less_equal_higher_priority_patient(self, _label,
                                                lhs_initials, rhs_initials,
                                                lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertTrue(lhs <= rhs)

    @parameterized.expand([
        ('same initials', 'PP', 'PP', 1002, 1000),
        ('incr initials', 'PP', 'QQ', 1002, 1000),
        ('decr initials', 'QQ', 'PP', 1002, 1000),
    ])
    def test_not_less_equal_lower_priority_patient(self, _label,
                                                   lhs_initials, rhs_initials,
                                                   lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs <= rhs)

    def test_not_greater_than_itself(self):
        patient = Patient('AM', 4041)
        self.assertFalse(patient > patient)

    def test_not_greater_than_shallow_copy(self):
        original = Patient('BN', 3074)
        duplicate = copy.copy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertFalse(original > duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertFalse(duplicate > original)

    def test_not_greater_than_deep_copy(self):
        original = Patient('CO', 1122)
        duplicate = copy.deepcopy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertFalse(original > duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertFalse(duplicate > original)

    def test_not_greater_than_pickling_clone(self):
        original = Patient('DP', 7970)
        duplicate = pickle.loads(pickle.dumps(original))
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertFalse(original > duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertFalse(duplicate > original)

    @parameterized.expand([
        ('same initials', 'XX', 'XX', 1001, 1001),
        ('incr initials', 'XX', 'YY', 1001, 1001),
        ('decr initials', 'YY', 'XX', 1001, 1001),
    ])
    def test_not_greater_than_other_same_priority_patient(
            self, _label,
            lhs_initials, rhs_initials, lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs > rhs)

    @parameterized.expand([
        ('same initials', 'WW', 'WW', 1000, 1002),
        ('incr initials', 'WW', 'ZZ', 1000, 1002),
        ('decr initials', 'ZZ', 'WW', 1000, 1002),
    ])
    def test_not_greater_than_higher_priority_patient(
            self, _label,
            lhs_initials, rhs_initials, lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs > rhs)

    @parameterized.expand([
        ('same initials', 'PP', 'PP', 1002, 1000),
        ('incr initials', 'PP', 'QQ', 1002, 1000),
        ('decr initials', 'QQ', 'PP', 1002, 1000),
    ])
    def test_greater_than_lower_priority_patient(self, _label,
                                                 lhs_initials, rhs_initials,
                                                 lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertTrue(lhs > rhs)

    def test_greater_than_or_equal_to_itself(self):
        patient = Patient('AM', 4041)
        self.assertTrue(patient >= patient)

    def test_greater_than_or_equal_to_shallow_copy(self):
        original = Patient('BN', 3074)
        duplicate = copy.copy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertTrue(original >= duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertTrue(duplicate >= original)

    def test_greater_than_or_equal_to_deep_copy(self):
        original = Patient('CO', 1122)
        duplicate = copy.deepcopy(original)
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertTrue(original >= duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertTrue(duplicate >= original)

    def test_greater_than_or_equal_to_pickling_clone(self):
        original = Patient('DP', 7970)
        duplicate = pickle.loads(pickle.dumps(original))
        with self.subTest(lhs='orig', rhs='copy'):
            self.assertTrue(original >= duplicate)
        with self.subTest(lhs='copy', rhs='orig'):
            self.assertTrue(duplicate >= original)

    @parameterized.expand([
        ('same initials', 'XX', 'XX', 1001, 1001),
        ('incr initials', 'XX', 'YY', 1001, 1001),
        ('decr initials', 'YY', 'XX', 1001, 1001),
    ])
    def test_not_greater_equal_other_same_priority_patient(
            self, _label,
            lhs_initials, rhs_initials, lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs >= rhs)

    @parameterized.expand([
        ('same initials', 'WW', 'WW', 1000, 1002),
        ('incr initials', 'WW', 'ZZ', 1000, 1002),
        ('decr initials', 'ZZ', 'WW', 1000, 1002),
    ])
    def test_not_greater_equal_higher_priority_patient(
            self, _label,
            lhs_initials, rhs_initials, lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertFalse(lhs >= rhs)

    @parameterized.expand([
        ('same initials', 'PP', 'PP', 1002, 1000),
        ('incr initials', 'PP', 'QQ', 1002, 1000),
        ('decr initials', 'QQ', 'PP', 1002, 1000),
    ])
    def test_greater_equal_lower_priority_patient(self, _label,
                                                  lhs_initials, rhs_initials,
                                                  lhs_priority, rhs_priority):
        lhs = Patient(lhs_initials, lhs_priority)
        rhs = Patient(rhs_initials, rhs_priority)
        self.assertTrue(lhs >= rhs)

    def test_order_comparison_reflects_priority_change(self):
        patients = [Patient('LZ', 10), Patient('MY', 20), Patient('NX', 30),
                    Patient('NK', 30), Patient('NS', 30), Patient('OW', 40),
                    Patient('OV', 40), Patient('PV', 50), Patient('QU', 60)]
        if patients != sorted(patients):
            raise Exception("initial ordering wrong, can't test reordering")

        # We will decrease QU's priority from 60 to 25, to be the third lowest.
        expected = [patients[0], patients[1], patients[8],
                    patients[2], patients[3], patients[4],
                    patients[5], patients[6], patients[7]]

        patients[8].priority -= 35
        if patients[8].priority != 25:
            raise Exception("couldn't change priority, can't test reordering")

        actual = sorted(patients)
        self.assertListEqual(actual, expected)


class TestOrderIndistinct(unittest.TestCase):
    """Tests for the OrderIndistinct class."""

    _VALUE_ARGS_WITHOUT_JUST_OBJ = [
        ('int', 42),
        ('str', 'ham'),
        ('list of str', ['foo', 'bar', 'baz', 'quux', 'foobar']),
        ('list of int', [10, 20, 30, 40, 50, 60, 70]),
        ('Fraction', Fraction(5, 9)),
        ('None', None),
    ]
    """Labeled values of, or containing, different types; but not object()."""

    _VALUE_ARGS = _VALUE_ARGS_WITHOUT_JUST_OBJ + [('just obj', object())]
    """Some labeled values of, or containing, different types."""

    _VALUE_ARGS_WITH_EXPECTED_REPR = [
        ('int', 42, 'OrderIndistinct(42)'),
        ('str', 'ham', "OrderIndistinct('ham')"),
        ('list of str',
        ['foo', 'bar', 'baz', 'quux', 'foobar'],
        "OrderIndistinct(['foo', 'bar', 'baz', 'quux', 'foobar'])"),
        ('list of int',
        [10, 20, 30, 40, 50, 60, 70],
        "OrderIndistinct([10, 20, 30, 40, 50, 60, 70])"),
        ('Fraction', Fraction(5, 9), 'OrderIndistinct(Fraction(5, 9))'),
        ('None', None, 'OrderIndistinct(None)'),
    ]
    """Labeled values and expected OrderIndistinct object reprs."""

    _DISTINCT_VALUE_PAIRS = [
        ('ints', 42, 76),
        ('strs', 'ham', 'foo'),
        ('lists of str', ['foo', 'bar'], ['foo', 'baz']),
        ('lists of int', [1, 2, 3, 4, 5], [1, 3, 4, 3, 5]),
        ('singletons', None, ...),
        ('just objs', object(), object()),
    ]
    """Labeled pairs of distinct values of, and containing, the same type."""

    _VALUE_SEQUENCES = [
        ('letters', ['Y', 'X', 'C', 'A', 'E', 'B', 'D']),
        ('ints', [4, 9, 3, 7, 5, 15, 0, 18, 19, 11, 12, 16, 17, 14, 1, 13, 8]),
        ('str lists', [
            ['ham', 'spam', 'eggs'],
            ['foo', 'bar', 'baz', 'quux', 'foobar'],
            ['Alice', 'Bob', 'Carol', 'Cassidy', 'Christine', 'Derek'],
        ]),
        ('just objs', [object(), object(), object(), object(), object()]),
    ]
    """Labeled sequences of values, for testing stable sorting."""

    __slots__ = ()

    def test_cannot_construct_with_no_arguments(self):
        """Passing less than 1 argument to the constructor raises TypeError."""
        with self.assertRaises(TypeError):
            OrderIndistinct()

    def test_cannot_construct_with_multiple_arguments(self):
        """Passing more than 1 argument to the constructor raises TypeError."""
        with self.assertRaises(TypeError):
            OrderIndistinct(10, 20)

    @parameterized.expand(_VALUE_ARGS)
    def test_can_construct_with_single_argument(self, _label, value):
        """Passing a single argument to the constructor works."""
        try:
            OrderIndistinct(value)
        except TypeError as error:  # Makes TypeError "FAIL" (not "ERROR").
            description = 'TypeError calling OrderIndistinct with one argument'
            msg_info = f'(message: {error})'
            self.fail(f'{description} {msg_info}')

    @parameterized.expand(_VALUE_ARGS_WITH_EXPECTED_REPR)
    def test_repr_shows_type_with_value_arg(self, _label, value, expected):
        """The repr looks like code that could've created the object."""
        oi = OrderIndistinct(value)
        actual = repr(oi)
        self.assertEqual(actual, expected)

    @parameterized.expand(_VALUE_ARGS_WITHOUT_JUST_OBJ)
    def test_repr_roundtrips_by_eval(self, _label, value):
        """The repr is Python code that when eval'd gives an equal object."""
        original = OrderIndistinct(value)
        copy = eval(repr(original))
        self.assertEqual(original, copy)

    @parameterized.expand(_VALUE_ARGS_WITH_EXPECTED_REPR)
    def test_repr_correct_in_derived_class(self, _label, value, base_expected):
        """The repr shows a derived-class name (and also the correct value)."""
        class Derived(OrderIndistinct): pass
        derived_expected = base_expected.replace('OrderIndistinct', 'Derived')
        oi = Derived(value)
        actual = repr(oi)
        self.assertEqual(actual, derived_expected)

    @parameterized.expand(_VALUE_ARGS)
    def test_value_attr_has_original_value_arg(self, _label, value):
        """A positional argument on construction writes the value attribute."""
        oi = OrderIndistinct(value)
        self.assertEqual(oi.value, value)

    @parameterized.expand(_VALUE_ARGS)
    def test_value_attr_has_original_value_keyword_arg(self, _label, value):
        """A value= keyword arg on construction writes the value attribute."""
        oi = OrderIndistinct(value=value)
        self.assertEqual(oi.value, value)

    @parameterized.expand(_VALUE_ARGS)
    def test_value_attribute_can_be_changed(self, _label, new_value):
        """The value attribute is read-write. Reads see earlier writes."""
        old_value = object()
        oi = OrderIndistinct(old_value)
        oi.value = new_value
        with self.subTest(comparison='!= old'):
            self.assertNotEqual(oi.value, old_value)
        with self.subTest(comparison='== new'):
            self.assertEqual(oi.value, new_value)

    def test_new_attributes_cannot_be_created(self):
        """Assigning to a nonexistent attribute raises AttributeError."""
        oi = OrderIndistinct(42)
        with self.assertRaises(AttributeError):
            oi.valur = 76  # Misspelling of "value".

    @parameterized.expand(_VALUE_ARGS)
    def test_we_get_a_new_object_even_with_the_same_value(self, _label, value):
        """
        Calling OrderIndistinct always constructs a new object.

        This behavior is important because OrderIndistinct is a mutable type.
        """
        first = OrderIndistinct(value)
        second = OrderIndistinct(value)
        self.assertIsNot(first, second)

    @parameterized.expand(_VALUE_ARGS)
    def test_equal_when_value_is_equal(self, _label, value):
        """From the same value argument, OrderIndistint objects are equal."""
        # In unittest tests, we usually use assertEqual/assertNotEqual, rather
        # than writing the == and != operators with assertTrue/assertFalse.
        # However, when testing the == and != operators themselves, some people
        # like to write them explicitly. This can help test for unusual, but
        # possible, bugs, if both == and != are meant to use __eq__ but don't.
        first = OrderIndistinct(value)
        second = OrderIndistinct(value)
        with self.subTest(comparison='=='):
            self.assertTrue(first == second)
        with self.subTest(comparison='!='):
            self.assertFalse(first != second)

    @parameterized.expand(_DISTINCT_VALUE_PAIRS)
    def test_not_equal_when_value_is_not_equal(self, _label, lhs, rhs):
        """
        From different value arguments, OrderIndistinct objects are unequal.
        """
        # See the comment in test_equal_when_value_is_equal on this technique.
        first = OrderIndistinct(lhs)
        second = OrderIndistinct(rhs)
        with self.subTest(comparison='=='):
            self.assertFalse(first == second)
        with self.subTest(comparison='!='):
            self.assertTrue(first != second)

    @parameterized.expand(_VALUE_ARGS)
    def test_not_less_with_same_value(self, _label, value):
        """From the same value argument, "<" is false."""
        first = OrderIndistinct(value)
        second = OrderIndistinct(value)
        self.assertFalse(first < second)  # No assertNotLess method.

    @parameterized.expand(_DISTINCT_VALUE_PAIRS)
    def test_not_less_with_different_values(self, _label, lhs, rhs):
        """From different value arguments, "<" is false."""
        first = OrderIndistinct(lhs)
        second = OrderIndistinct(rhs)
        self.assertFalse(first < second)  # No assertNotLess method.

    @parameterized.expand(_VALUE_ARGS)
    def test_not_greater_with_same_value(self, _label, value):
        """From the same value argument, ">" is false."""
        first = OrderIndistinct(value)
        second = OrderIndistinct(value)
        self.assertFalse(first > second)  # No assertNotGreater method.

    @parameterized.expand(_DISTINCT_VALUE_PAIRS)
    def test_not_greater_with_different_values(self, _label, lhs, rhs):
        """From different value arguments, ">" is false."""
        first = OrderIndistinct(lhs)
        second = OrderIndistinct(rhs)
        self.assertFalse(first > second)  # No assertNotGreater method.

    @parameterized.expand(_VALUE_ARGS)
    def test_less_or_equal_with_same_value(self, _label, value):
        """From the same value argument, "<=" is true."""
        first = OrderIndistinct(value)
        second = OrderIndistinct(value)
        self.assertLessEqual(first, second)

    @parameterized.expand(_DISTINCT_VALUE_PAIRS)
    def test_not_less_or_equal_with_different_values(self, _label, lhs, rhs):
        """From different value arguments, "<=" is false."""
        first = OrderIndistinct(lhs)
        second = OrderIndistinct(rhs)
        self.assertFalse(first <= second)  # No assertNotLessEqual method.

    @parameterized.expand(_VALUE_ARGS)
    def test_greater_or_equal_with_same_value(self, _label, value):
        """With OrderIndistincts of the same value argument, ">=" is true."""
        first = OrderIndistinct(value)
        second = OrderIndistinct(value)
        self.assertGreaterEqual(first, second)

    @parameterized.expand(_DISTINCT_VALUE_PAIRS)
    def test_not_greater_or_equal_with_different_values(self,
                                                        _label, lhs, rhs):
        """From different value arguments, ">=" is false."""
        first = OrderIndistinct(lhs)
        second = OrderIndistinct(rhs)
        self.assertFalse(first >= second)  # No assertNotLessEqual method.

    def test_not_hashable(self):
        """
        Calling hash on an OrderIndistinct raises TypeError.

        This behavior is important because OrderIndistinct is a mutable type.
        """
        oi = OrderIndistinct(42)
        with self.assertRaises(TypeError):
            hash(oi)

    @parameterized.expand(_VALUE_SEQUENCES)
    def test_not_rearranged_by_sorted_builtin(self, _label, values):
        """sorted is stable, so it preserves OrderIndistinct objects' order."""
        before_sorting = [OrderIndistinct(x) for x in values]
        after_sorting = sorted(before_sorting)
        self.assertListEqual(before_sorting, after_sorting)

    @parameterized.expand(_VALUE_SEQUENCES)
    def test_not_rearranged_by_list_sort_method(self, _label, values):
        """
        list.sort is stable, so it preserves OrderIndistict objects' order.
        """
        original = [OrderIndistinct(x) for x in values]
        copy = original[:]
        copy.sort()
        self.assertListEqual(original, copy)


if __name__ == '__main__':
    unittest.main()
