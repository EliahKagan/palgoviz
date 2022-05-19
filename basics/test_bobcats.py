#!/usr/bin/env python

"""Tests for the bobcats module."""

from decimal import Decimal
from fractions import Fraction
import unittest

from bobcats import Bobcat, FierceBobcat


class TestBobcat(unittest.TestCase):
    """Tests for the Bobcat class."""

    __slots__ = ()

    def test_names_must_be_strings(self):
        with self.assertRaises(TypeError):
            Bobcat(0)

    def test_names_must_be_nonempty(self):
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

    def test_same_named_bobcats_are_equal(self):
        first = Bobcat('Countess von Willdebrandt')
        second = Bobcat('Countess von Willdebrandt')
        self.assertEqual(first, second)

    def test_differently_named_bobcats_are_not_equal(self):
        first = Bobcat('Countess von Willdebrandt')
        second = Bobcat('Countess von Willdebruvft')
        self.assertNotEqual(first, second)

    def test_bobcats_are_not_equal_to_non_bobcats(self):
        # TODO: Use subTest.
        bobcat = Bobcat('Countess von Willdebrandt')
        non_bobcat = 'Countess von Willdebrandt'
        self.assertNotEqual(bobcat, non_bobcat)
        self.assertNotEqual(non_bobcat, bobcat)

    def test_same_named_bobcats_hash_the_same(self):
        first = Bobcat('Countess von Willdebrandt')
        second = Bobcat('Countess von Willdebrandt')
        self.assertEqual(hash(first), hash(second))

    def test_name_attribute_has_name(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        self.assertEqual(bobcat.name, 'Countess von Willdebrandt')

    def test_name_attribute_is_read_only(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        with self.assertRaises(AttributeError):
            bobcat.name = 'Ekaterina'

    def test_new_attributes_cannot_be_created(self):
        bobcat = Bobcat('Countess von Willdebrandt')
        with self.assertRaises(AttributeError):
            bobcat.namr = 'Ekaterina'  # Misspelling of "name".

    def test_bobcats_work_in_hash_based_containers(self):
        b1 = Bobcat('Countess von Willdebrandt')
        b2 = Bobcat('Countess von Willdebruvft')
        b3 = Bobcat('Countess von Willdebrandt')  # Same as b1.
        b4 = Bobcat('Bob')
        b5 = Bobcat('Ekaterina')
        b6 = Bobcat('T\'plak\'\'H"my\\0qQ\x00g\\n\nh"\\')
        b7 = Bobcat('Ekaterina')  # Same as b5.
        b8 = Bobcat('Countess von Willdebrandt')  # Same as b1, again.

        d = dict.fromkeys([b1, b2, b3, b4, b5, b6, b7, b8])
        self.assertListEqual(list(d), [b1, b2, b4, b5, b6])

    #@unittest.skip("We haven't decided if name mangling is justified here.")
    def test_private_attribute_avoids_derived_class_nonpublic_clash(self):
        """
        This intends to test that Bobcat uses __name instead of _name (1 of 2).

        Even if leading double-underscore names weren't mangled, no clash would
        be expected here, since the derived class attribute name is different.
        """
        class NameRememberingBobcat(Bobcat):
            def __init__(self, own_name, name):
                super().__init__(own_name)
                self._name = name  # Same-named leading _ (single) attribute.

            @property
            def remembered_name(self):
                return self._name

        # TODO: Use subTest.
        bobcat = NameRememberingBobcat('Ekaterina', 'Phineas')
        self.assertEqual(bobcat.name, 'Ekaterina')
        self.assertEqual(bobcat.remembered_name, 'Phineas')
        self.assertEqual(bobcat._Bobcat__name, 'Ekaterina')
        self.assertEqual(bobcat._name, 'Phineas')
        self.assertFalse(hasattr(bobcat, '_NameRememberingBobcat__name'))

    #@unittest.skip("We haven't decided if name mangling is justified here.")
    def test_private_attribute_avoids_derived_class_mangled_clash(self):
        """
        This intends to test that Bobcat uses __name instead of _name (2 of 2).

        The base class and derived class attributes are both written as exactly
        __name, yet there is no clash, because they are mangled differently.
        """
        class NameRememberingBobcat(Bobcat):
            def __init__(self, own_name, name):
                super().__init__(own_name)
                self.__name = name  # Same-named leading __ (double) attribute.

            @property
            def remembered_name(self):
                return self.__name

        # TODO: Use subTest.
        bobcat = NameRememberingBobcat('Ekaterina', 'Phineas')
        self.assertEqual(bobcat.name, 'Ekaterina')
        self.assertEqual(bobcat.remembered_name, 'Phineas')
        self.assertEqual(bobcat._Bobcat__name, 'Ekaterina')
        self.assertEqual(bobcat._NameRememberingBobcat__name, 'Phineas')
        self.assertFalse(hasattr(bobcat, '_name'))


class TestFierceBobcat(unittest.TestCase):
    """Tests for the FierceBobcat class."""

    __slots__ = ()

    def test_fierceness_cutoff_is_9000(self):
        self.assertEqual(FierceBobcat.FIERCENESS_CUTOFF, 9000)

    def test_names_must_be_strings(self):
        with self.assertRaises(TypeError):
            FierceBobcat(0, 10_000)

    def test_names_must_be_nonempty(self):
        with self.assertRaises(ValueError):
            FierceBobcat('', 10_000)

    def test_fierceness_must_be_numeric(self):
        with self.assertRaises(TypeError):
            FierceBobcat('Mean Bob', '10000')

    def test_fierceness_must_not_be_complex(self):
        with self.assertRaises(TypeError):
            FierceBobcat('Mean Bob', 9500 + 444j)

    def test_fierceness_must_not_be_complex_even_if_zero_imaginary_part(self):
        with self.assertRaises(TypeError):
            FierceBobcat('Mean Bob', 9500 + 0j)

    def test_fierceness_must_not_be_decimal(self):
        """
        Fierceness's type must allow arithmetic with other numeric types.

        Fractional values of float are OK, but not the Decimal type.
        """
        with self.assertRaises(TypeError):
            FierceBobcat('Mean Bob', Decimal('9534.22718'))

    def test_fierceness_must_not_be_under_9000(self):
        with self.assertRaises(ValueError):
            FierceBobcat('Mean Bob', 8999)

    def test_fierceness_must_not_be_even_slightly_under_9000(self):
        with self.assertRaises(ValueError):
            FierceBobcat('Mean Bob', 8999.99999)

    def test_fierceness_must_actually_be_over_9000(self):
        with self.assertRaises(ValueError):
            FierceBobcat('Mean Bob', 9000)

    def test_the_only_problem_with_bools_is_they_are_not_fierce_enough(self):
        # TODO: Use subTest or other parameterization.
        with self.assertRaises(ValueError):
            FierceBobcat('Mean Bob', False)
        with self.assertRaises(ValueError):
            FierceBobcat('Mean Bob', True)

    def test_fierce_bobcats_are_bobcats(self):
        bobcat = FierceBobcat('Mean Bob', 9001)
        self.assertIsInstance(bobcat, Bobcat)

    def test_repr_is_well_formed(self):
        """Unlike Bobcat, FierceBobcat's repr shows parameter names."""
        expected_repr = "FierceBobcat(name='Mean Bob', fierceness=9500)"
        bobcat = FierceBobcat('Mean Bob', 9500)
        self.assertEqual(repr(bobcat), expected_repr)

    def test_repr_uses_reprs_of_both_name_and_fierceness(self):
        expected_repr = (
            "FierceBobcat(name='Mean Bob', fierceness=Fraction(9090000, 1007))"
        )
        bobcat = FierceBobcat('Mean Bob', Fraction(9_090_000, 1007))
        self.assertEqual(repr(bobcat), expected_repr)

    def test_repr_roundtrips_via_eval(self):
        bobcat = FierceBobcat('Mean Bob', 9500)
        copy = eval(repr(bobcat))
        self.assertEqual(bobcat, copy)

    def test_repr_is_well_formed_when_name_is_weird(self):
        weird_name = 'G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\'
        expected_repr = (
            R"""FierceBobcat(name='G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\',"""
            ' fierceness=9670)'
        )
        bobcat = FierceBobcat(weird_name, 9670)
        self.assertEqual(repr(bobcat), expected_repr)

    def test_repr_roundtrips_via_eval_when_name_is_weird(self):
        weird_name = 'G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\'
        bobcat = FierceBobcat(weird_name, fierceness=9670)
        copy = eval(repr(bobcat))
        self.assertEqual(bobcat, copy)

    def test_str_good_to_announce_bobcat_at_fancy_parties(self):
        """End users and partygoers are best not told of all the fierceness."""
        bobcat = FierceBobcat('Mean Bob', 9500)
        self.assertEqual(str(bobcat), 'Mean Bob the bobcat')

    def test_str_good_to_announce_weird_named_bobcat_at_fancy_parties(self):
        weird_name = 'G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\'
        expected_str = 'G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\ the bobcat'
        bobcat = FierceBobcat(weird_name, fierceness=9670)
        self.assertEqual(str(bobcat), expected_str)

    def test_same_name_and_fierceness_bobcats_are_equal(self):
        first = FierceBobcat('Mean Bob', 9500)
        second = FierceBobcat('Mean Bob', 9500)
        self.assertEqual(first, second)

    def test_bobcats_differing_only_by_type_of_fierceness_are_equal(self):
        """The same name and fierceness *value* are sufficient for equality."""
        int_bob = FierceBobcat('Mean Bob', 9500)
        float_bob = FierceBobcat('Mean Bob', 9500.0)
        fraction_bob = FierceBobcat('Mean Bob', Fraction(9500, 1))

        # TODO: Use subTest or other parameterization.
        self.assertEqual(int_bob, float_bob)
        self.assertEqual(int_bob, fraction_bob)
        self.assertEqual(float_bob, int_bob)
        self.assertEqual(float_bob, fraction_bob)
        self.assertEqual(fraction_bob, int_bob)
        self.assertEqual(fraction_bob, float_bob)

    def test_bobcats_differing_in_both_name_and_fierceness_are_not_equal(self):
        first = FierceBobcat('Mean Bob', 9500)
        second = FierceBobcat('Ekaterina II', 10_447.2)
        self.assertNotEqual(first, second)

    def test_differently_named_bobcats_are_not_equal(self):
        first = FierceBobcat('Mean Bob', 9500)
        second = FierceBobcat('Mane Bob', 9500)
        self.assertNotEqual(first, second)

    def test_differently_fierce_bobcats_are_not_equal(self):
        first = FierceBobcat('Mean Bob', 9500)
        second = FierceBobcat('Mean Bob', 9499)
        self.assertNotEqual(first, second)

    def test_fierce_bobcats_are_not_equal_to_regular_bobcats(self):
        # TODO: Use subTest.
        regular = Bobcat('Countess von Willdebrandt')
        fierce = FierceBobcat('Countess von Willdebrandt', 17_346_802)
        self.assertNotEqual(fierce, regular)
        self.assertNotEqual(regular, fierce)

    def test_fierce_bobcats_are_not_equal_to_non_bobcats(self):
        # TODO: Use subTest.
        bobcat = FierceBobcat('Mean Bob', 9500)
        non_bobcat = ('Mean Bob', 9500)
        self.assertNotEqual(bobcat, non_bobcat)
        self.assertNotEqual(non_bobcat, bobcat)

    def test_bobcats_of_same_name_and_fierceness_hash_the_same(self):
        first = FierceBobcat('Mean Bob', 9500)
        second = FierceBobcat('Mean Bob', 9500)
        self.assertEqual(hash(first), hash(second))

    def test_bobcats_differing_only_by_type_of_fierceness_hash_the_same(self):
        int_bob = FierceBobcat('Mean Bob', 9500)
        float_bob = FierceBobcat('Mean Bob', 9500.0)
        fraction_bob = FierceBobcat('Mean Bob', Fraction(9500, 1))

        int_bob_hash = hash(int_bob)

        # TODO: Use subTest or other parameterization.
        self.assertEqual(hash(float_bob), int_bob_hash)
        self.assertEqual(hash(fraction_bob), int_bob_hash)

    def test_name_attribute_has_name(self):
        bobcat = FierceBobcat('Mean Bob', 9500)
        self.assertEqual(bobcat.name, 'Mean Bob')

    def test_name_attribute_is_read_only(self):
        bobcat = FierceBobcat('Mean Bob', 9500)
        with self.assertRaises(AttributeError):
            bobcat.name = 'Catbert'

    def test_fierceness_attribute_has_fierceness(self):
        bobcat = FierceBobcat('Mean Bob', 9500)
        self.assertEqual(bobcat.fierceness, 9500)

    def test_fierceness_attribute_is_read_only(self):
        bobcat = FierceBobcat('Mean Bob', 9500)
        with self.assertRaises(AttributeError):
            bobcat.fierceness = 9499

    def test_new_attributes_cannot_be_created(self):
        bobcat = FierceBobcat('Mean Bob', 9500)
        with self.assertRaises(AttributeError):
            bobcat.namr = 'Catbert'  # Misspelling of "name".

    def test_fierce_bobcats_work_in_hash_based_containers(self):
        fb1 = FierceBobcat('Mean Bob', 9500)
        fb2 = FierceBobcat('Mean Bob', 9499)
        fb3 = FierceBobcat('Ekaterina II', 9500)
        fb4 = FierceBobcat('Ekaterina II', 9499)
        fb5 = FierceBobcat('Mean Bob', Fraction(9500, 1))  # Same as fb1.
        fb6 = FierceBobcat('Mean Bob', 9500)  # Same as fb1, again.
        fb7 = FierceBobcat('Mean Bob', 9500.0)  # Same as fb1, yet again.
        fb8 = FierceBobcat('G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\', 9670)
        fb9 = FierceBobcat('Ekaterina II', 9499.0)  # Same as fb4.

        d = dict.fromkeys([fb1, fb2, fb3, fb4, fb5, fb6, fb7, fb8, fb9])
        self.assertListEqual(list(d), [fb1, fb2, fb3, fb4, fb8])

    def test_fierce_and_regular_bobcats_work_in_hash_based_containers(self):
        fb1 = FierceBobcat('Mean Bob', 9500)
        b1 = Bobcat('Countess von Willdebrandt')
        fb2 = FierceBobcat('Mean Bob', 9499)
        b2 = Bobcat('Countess von Willdebruvft')
        fb3 = FierceBobcat('Countess von Willdebrandt', 9500)
        b3 = Bobcat('Countess von Willdebrandt')  # Same as b1.
        b4 = Bobcat('Mean Bob')
        fb4 = FierceBobcat('Countess von Willdebrandt', 9499)
        fb5 = FierceBobcat('Mean Bob', Fraction(9500, 1))  # Same as fb1.
        fb6 = FierceBobcat('Mean Bob', 9500)  # Same as fb1, again.
        fb7 = FierceBobcat('Mean Bob', 9500.0)  # Same as fb1, yet again.
        fb8 = FierceBobcat('G\'bhuj\'\'H"my\\0qQ\x00g\\n\nh"\\', 9670)
        fb9 = FierceBobcat('Countess von Willdebrandt', 9499.0)  # Same as fb4.
        b5 = Bobcat('Countess von Willdebrandt')  # Same as b1, again.

        d = dict.fromkeys(
            [fb1, b1, fb2, b2, fb3, b3, b4, fb4, fb5, fb6, fb7, fb8, fb9, b5])

        self.assertListEqual(list(d), [fb1, b1, fb2, b2, fb3, b4, fb4, fb8])


if __name__ == '__main__':
    unittest.main()
