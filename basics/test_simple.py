"""Tests for the simple functions in simple.py."""

import fractions
import io
import sys
import unittest

from simple import alert, answer, bail_if, is_sorted, parse_yes_no


class TestAnswer(unittest.TestCase):
    """Tests for the answer function."""

    __slots__ = ()

    def test_the_answer_is_42(self):
        result = answer()
        self.assertEqual(result, 42)

    def test_the_answer_is_an_int(self):
        result = answer()
        self.assertIsInstance(result, int)


class TestParseYesNo(unittest.TestCase):
    """Tests for the parse_yes_no function."""

    __slots__ = ()

    def test_yes_parses_true(self):
        self.assertTrue(parse_yes_no('yes'))

    def test_no_parses_false(self):
        self.assertFalse(parse_yes_no('no'))

    def test_capitalized_yes_parses_true(self):
        self.assertTrue(parse_yes_no('Yes'))

    def test_capitalized_no_parses_false(self):
        self.assertFalse(parse_yes_no('No'))

    def test_text_other_than_yes_or_no_fails_to_parse(self):
        with self.assertRaises(ValueError):
            parse_yes_no('ness')


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
