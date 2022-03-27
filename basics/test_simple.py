#!/usr/bin/env python

"""Tests for the simple code in simple.py."""

from fractions import Fraction
import io
import sys
import unittest

from parameterized import parameterized, parameterized_class

from simple import (
    MY_NONE,
    Squarer,
    Toggle,
    make_squarer,
    MulSquarer,
    PowSquarer,
    Widget,
    answer,
    is_sorted,
    alert,
    bail_if,
    make_toggle)


class TestMyNone(unittest.TestCase):
    """The MY_NONE constant doesn't need any tests. Here's one anyway."""

    def test_my_none_is_none(self):
        self.assertIsNone(MY_NONE)


class TestWidget(unittest.TestCase):
    """Tests for the Widget class."""

    def setUp(self):
        """Make a Widget for testing."""
        self.widget = Widget('vast', 'mauve')  # Arrange

    def test_size_attribute_has_size(self):
        self.assertEqual(self.widget.size, 'vast')

    def test_color_attribute_has_color(self):
        self.assertEqual(self.widget.color, 'mauve')

    def test_size_can_be_changed(self):
        self.widget.size = 'just barely visible'
        self.assertEqual(self.widget.size, 'just barely visible')

    def test_color_can_be_changed(self):
        self.widget.color = 'royal purple'  # Act.
        self.assertEqual(self.widget.color, 'royal purple')  # Assert.

    def test_new_attributes_cannot_be_added(self):
        with self.assertRaises(AttributeError):
            self.widget.favorite_desert = 'Sahara'


class TestAnswer(unittest.TestCase):
    """Test the answer() function."""

    def test_the_answer_is_42(self):
        answer_to_the_question = answer()
        self.assertEqual(answer_to_the_question, 42)

    def test_the_answer_is_an_int(self):
        answer_to_the_question = answer()
        self.assertIsInstance(answer_to_the_question, int)


class TestIsSorted(unittest.TestCase):
    """Tests for the is_sorted function."""

    def test_empty_list_is_sorted(self):
        items = []
        self.assertTrue(is_sorted(items))

    def test_empty_generator_is_sorted(self):
        items = (x for x in ())
        self.assertTrue(is_sorted(items))

    def test_one_element_list_is_sorted(self):
        items = [76]
        self.assertTrue(is_sorted(items))

    def test_one_element_generator_is_sorted(self):
        items = (x for x in (76,))
        self.assertTrue(is_sorted(items))

    def test_ascending_two_element_list_is_sorted(self):
        items = ['a', 'b']
        self.assertTrue(is_sorted(items))

    def test_descending_two_element_list_is_not_sorted(self):
        with self.subTest(kind='strings'):
            items = ['b', 'a']
            self.assertFalse(is_sorted(items))

        with self.subTest(kind='integers'):
            items = [3, 2]
            self.assertFalse(is_sorted(items))

    def test_descending_two_element_generator_is_not_sorted(self):
        with self.subTest(kind='strings'):
            items = (x for x in ('b', 'a'))
            self.assertFalse(is_sorted(items))

        with self.subTest(kind='integers'):
            items = (x for x in (3, 2))
            self.assertFalse(is_sorted(items))

    def test_ascending_two_element_generator_is_sorted(self):
        items = (ch for ch in 'ab')
        self.assertTrue(is_sorted(items))

    def test_equal_two_element_list_is_sorted(self):
        items = ['a', 'a']
        self.assertTrue(is_sorted(items))

    def test_equal_two_element_generator_is_sorted(self):
        items = (ch for ch in 'aa')
        self.assertTrue(is_sorted(items))

    def test_sorted_short_but_nontrivial_list_is_sorted(self):
        items = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
        self.assertTrue(is_sorted(items))

    def test_unsorted_short_but_nontrivial_is_unsorted(self):
        items = ['bar', 'eggs', 'foo', 'ham', 'foobar', 'quux', 'baz', 'spam']
        self.assertFalse(is_sorted(items))


class TestAlert(unittest.TestCase):
    """Tests for the alert function."""

    def setUp(self):
        """Redirect standard error."""
        self._old_err = sys.stderr
        self._my_stderr = sys.stderr = io.StringIO()

    def tearDown(self):
        """Restore original standard error."""
        sys.stderr = self._old_err

    @parameterized.expand([
        ("Wall is still up.", "alert: Wall is still up.\n"),
        ("in your base.", "alert: in your base.\n"),
        ("killing your dudes.", "alert: killing your dudes.\n"),
        ('refusing to say hello', 'alert: refusing to say hello\n'),
        ('3609 squirrels complained', 'alert: 3609 squirrels complained\n'),
        ('boycott whalebone skis', 'alert: boycott whalebone skis\n'),
    ])
    def test_alert_and_newline_are_printed_with_string(self, message, expected):
        alert(message)
        self.assertEqual(self._actual, expected)

    def test_alert_with_nonstring_message_prints_str_of_message(self):
        message = Fraction(2, 3)
        expected = "alert: 2/3\n"
        alert(message)
        self.assertEqual(self._actual, expected)

    @property
    def _actual(self):
        """Result printed by alert()."""
        return self._my_stderr.getvalue()


class TestBailIf(unittest.TestCase):
    """Tests for the bail_if function."""

    def test_bails_if_truthy(self):
        for value in (True, 1, 1.1, 'hello', object()):
            with self.subTest(value=value):
                with self.assertRaises(SystemExit) as cm:
                    bail_if(value)
                self.assertEqual(cm.exception.code, 1)

    def test_does_not_bail_if_falsey(self):
        for value in (False, 0, 0.0, '', None):
            with self.subTest(value=value):
                try:
                    bail_if(value)
                except SystemExit:
                    self.fail("Bailed although condition was falsey.")


@parameterized_class(('name', 'implementation'), [
    ('Mul', MulSquarer),
    ('Pow', PowSquarer),
    ('func', staticmethod(make_squarer)),
])
class TestAllSquarers(unittest.TestCase):
    """Tests for any kind of Squarer."""

    @parameterized.expand([
        ('pos_0', 0, 0),
        ('pos_1', 1, 1),
        ('pos_2', 2, 4),
        ('pos_3', 3, 9),
    ])
    def test_positive_ints_are_squared(self, _name, num, expected):
        squarer = self.implementation()
        self.assertEqual(squarer(num), expected)

    @parameterized.expand([
        ('pos_0.0', 0.0, 0.0),
        ('pos_1.0', 1.0, 1.0),
        ('pos_2.2', 2.2, 4.84),
        ('pos_3.1', 3.1, 9.61),
    ])
    def test_positive_floats_are_squared(self, _name, num, expected):
        squarer = self.implementation()
        self.assertAlmostEqual(squarer(num), expected)

    @parameterized.expand([
        ('neg_1', -1, 1),
        ('neg_2', -2, 4),
        ('neg_3', -3, 9),
        ('neg_4', -4, 16),
    ])
    def test_negative_ints_are_squared(self, _name, num, expected):
        squarer = self.implementation()
        self.assertEqual(squarer(num), expected)

    @parameterized.expand([
        ('neg_1.2', -1.2, 1.44),
        ('neg_1.0', -1.0, 1.0),
        ('neg_2.2', -2.2, 4.84),
        ('neg_3.1', -3.1, 9.61),
    ])
    def test_negative_floats_are_squared(self, _name, num, expected):
        squarer = self.implementation()
        self.assertAlmostEqual(squarer(num), expected)


class TestSquarerClasses(unittest.TestCase):
    """Tests for the custom Squarer classes."""

    _SQUARERS = [
        ('Mul', MulSquarer),
        ('Pow', PowSquarer),
    ]

    @parameterized.expand([
        ('Mul', MulSquarer, 'MulSquarer()'),
        ('Pow', PowSquarer, 'PowSquarer()'),
    ])
    def test_repr(self, _name, impl, expected):
        """repr shows type and looks like Python code."""
        squarer = impl()
        self.assertEqual(repr(squarer), expected)

    @parameterized.expand(_SQUARERS)
    def test_squarer_is_a_squarer(self, _name, impl):
        squarer = impl()
        self.assertIsInstance(squarer, Squarer)

    @parameterized.expand(_SQUARERS)
    def test_squarers_of_same_type_are_equal(self, _name, impl):
        squarer1 = impl()
        squarer2 = impl()
        self.assertEqual(squarer1, squarer2)

    @parameterized.expand([
        ('Mul, Pow', MulSquarer, PowSquarer),
        ('Pow, Mul', PowSquarer, MulSquarer),
    ])
    def test_squarers_of_different_types_are_not_equal(self, _name,
                                                       impl1, impl2):
        squarer1 = impl1()
        squarer2 = impl2()
        self.assertNotEqual(squarer1, squarer2)

    @parameterized.expand(_SQUARERS)
    def test_squarers_of_same_type_hash_equal(self, _name, impl):
        squarer1 = impl()
        squarer2 = impl()
        self.assertEqual(hash(squarer1), hash(squarer2))


class TestMakeToggle(unittest.TestCase):
    """Test make_toggle function."""

    impl = staticmethod(make_toggle)

    def test_start_true_returns_true_on_first_call(self):
        tf = self.impl(True)
        self.assertIs(tf(), True)

    def test_start_false_returns_false_on_first_call(self):
        ft = self.impl(False)
        self.assertIs(ft(), False)

    def test_start_true_cycles_true_false(self):
        expected_results = [True, False] * 5
        tf = self.impl(True)

        for call_number, expected in enumerate(expected_results, 1):
            with self.subTest(call=call_number):
                self.assertIs(tf(), expected)

    def test_start_false_cycles_false_true(self):
        expected_results = [False, True] * 5
        ft = self.impl(False)

        for call_number, expected in enumerate(expected_results, 1):
            with self.subTest(call=call_number):
                self.assertIs(ft(), expected)

    def test_raises_TypeError_if_nonbool_is_passed(self):
        for value in (0, 1, 0.0, 1.1, '', 'j3j', None, object()):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.impl(value)


class TestToggleClass(TestMakeToggle):
    """Test Toggle class."""

    impl = Toggle

    def test_repr_true(self):
        tf = self.impl(True)
        self.assertEqual(repr(tf), 'Toggle(True)')

    def test_repr_false(self):
        ft = self.impl(False)
        self.assertEqual(repr(ft), 'Toggle(False)')

    def test_repr_cycle_start_true(self):
        expected_results = ['Toggle(False)', 'Toggle(True)'] * 5
        tf = self.impl(True)

        for call_number, expected in enumerate(expected_results, 1):
            with self.subTest(call=call_number):
                tf()
                self.assertEqual(repr(tf), expected)

    def test_repr_cycle_start_false(self):
        expected_results = ['Toggle(True)', 'Toggle(False)'] * 5
        ft = self.impl(False)

        for call_number, expected in enumerate(expected_results, 1):
            with self.subTest(call=call_number):
                ft()
                self.assertEqual(repr(ft), expected)

    # FIXME: Decide on, and carry out, one of the following:
    #
    #  (1) Give test_repr_cycle_start_true and test_repr_cycle_start_false
    #      more descriptive names that make claims about what they are testing.
    #
    #  (2) Consolidate both of them into one method, decorated with
    #      @parameterized.expand.


if __name__ == '__main__':
    unittest.main()
