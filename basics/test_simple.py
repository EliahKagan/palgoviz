"""Tests for the simple functions in simple.py."""

import contextlib
import io
import sys
import unittest

from simple import answer, die, is_sorted


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


class TestDie(unittest.TestCase):
    """Tests for the die function."""

    __slots__ = ('_old_argv', '_old_stderr', '_stderr')

    def setUp(self):
        """Monkey-patch command-line arguments and standard error."""
        self._old_argv = sys.argv
        self._old_stderr = sys.stderr
        sys.argv = ['PROGNAME']
        sys.stderr = self._stderr = io.StringIO()

    def tearDown(self):
        """Restore original command-line arguments and standard error."""
        sys.stderr = self._old_stderr
        sys.argv = self._old_argv

    def test_system_exit_is_attempted_with_status_1(self):
        with self.assertRaises(SystemExit) as context:
            die('the parrot is too badly stunned')

        self.assertEqual(context.exception.code, 1)

    def test_prefixed_message_is_printed_to_stderr(self):
        with contextlib.suppress(SystemExit):
            die('the parrot is too badly stunned')

        output = self._stderr.getvalue()

        self.assertEqual(output,
                         'PROGNAME: error: the parrot is too badly stunned\n')


if __name__ == '__main__':
    unittest.main()
