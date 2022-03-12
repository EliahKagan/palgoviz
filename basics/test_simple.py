#!/usr/bin/env python

"""Tests for the simple code in simple.py."""

import fractions
import io
import sys
import unittest

from simple import MY_NONE, Widget, alert, answer, bail_if, is_sorted


class TestMyNone(unittest.TestCase):
    """The MY_NONE constant doesn't need any tests. Here's one anyway."""

    __slots__ = ()

    def test_my_none_is_none(self):
        self.assertIsNone(MY_NONE)


# TODO: Extract common code to a setUp method.
class TestWidget(unittest.TestCase):
    """Tests for the Widget class."""

    __slots__ = ()

    def test_size_attribute_has_size(self):
        widget = Widget('vast', 'mauve')
        self.assertEqual(widget.size, 'vast')

    def test_color_attribute_has_color(self):
        widget = Widget('vast', 'mauve')
        self.assertEqual(widget.color, 'mauve')

    def test_size_can_be_changed(self):
        widget = Widget('vast', 'mauve')
        widget.size = 'just barely visible'
        self.assertEqual(widget.size, 'just barely visible')

    def test_color_can_be_changed(self):
        widget = Widget('vast', 'mauve')
        widget.color = 'royal purple'
        self.assertEqual(widget.color, 'royal purple')

    def test_new_attributes_cannot_be_added(self):
        widget = Widget('vast', 'mauve')
        with self.assertRaises(AttributeError):
            widget.favorite_desert = 'Sahara'


class TestAnswer(unittest.TestCase):
    """Tests for the answer function."""

    __slots__ = ()

    def test_the_answer_is_42(self):
        result = answer()
        self.assertEqual(result, 42)

    def test_the_answer_is_an_int(self):
        result = answer()
        self.assertIsInstance(result, int)


class TestIsSorted(unittest.TestCase):
    """Tests for the is_sorted function."""

    __slots__ = ()

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

    def test_ascending_two_element_generator_is_sorted(self):
        items = (ch for ch in 'ab')
        self.assertTrue(is_sorted(items))

    def test_equal_two_element_list_is_sorted(self):
        items = ['a', 'a']
        self.assertTrue(is_sorted(items))

    def test_equal_two_element_generator_is_sorted(self):
        items = (ch for ch in 'aa')
        self.assertTrue(is_sorted(items))

    def test_descending_two_element_list_is_not_sorted(self):
        items = ['b', 'a']
        self.assertFalse(is_sorted(items))

    def test_descending_two_element_generator_is_not_sorted(self):
        items = ['b', 'a']
        self.assertFalse(is_sorted(items))

    def test_sorted_short_but_nontrivial_list_is_sorted(self):
        items = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
        self.assertTrue(is_sorted(items))

    def test_unsorted_short_but_nontrivial_list_is_not_sorted(self):
        items = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'quux', 'spam', 'ham']
        self.assertFalse(is_sorted(items))


class TestAlert(unittest.TestCase):
    """Tests for the alert function."""

    __slots__ = ('_old_stderr', '_stderr')

    def setUp(self):
        """Monkey-patch ("redirect") standard error."""
        self._old_stderr = sys.stderr
        self._stderr = sys.stderr = io.StringIO()

    def tearDown(self):
        """Restore standard error."""
        sys.stderr = self._old_stderr

    def test_strings_are_printed_with_alert_prefix_and_newline(self):
        """When message is a string, it is placed literally in the output."""
        alert('the parrot is too badly stunned')
        self.assertEqual(self._out, 'alert: the parrot is too badly stunned\n')

    def test_str_not_repr_is_printed_with_alert_prefix_and_newline(self):
        """When message is not a string, it is converted with str, not repr."""
        alert(fractions.Fraction(3, 2))
        self.assertEqual(self._out, 'alert: 3/2\n')

    @property
    def _out(self):
        """The text written to standard error."""
        return self._stderr.getvalue()


class TestBailIf(unittest.TestCase):
    """Tests or the bail_if function."""

    __slots__ = ()

    def test_exits_on_literal_true_condition(self):
        with self.assertRaises(SystemExit):
            bail_if(True)

    def test_no_exit_on_literal_false_condition(self):
        try:
            bail_if(False)
        except SystemExit:
            self.fail('bail_if raised SystemExit when given False condition')

    def test_exits_on_truthy_condition(self):
        with self.assertRaises(SystemExit):
            bail_if('0')

    def test_no_exit_on_falsy_condition(self):
        try:
            bail_if('')
        except SystemExit:
            self.fail("bail_if raised SystemExit when passed the empty string")


if __name__ == '__main__':
    unittest.main()
