#!/usr/bin/env python

"""Tests for context managers in context.py."""

import contextlib
import io
import sys
import unittest

from parameterized import parameterized

import context


class _FakeError(Exception):
    """Fake exception, for testing."""


class _NonRedirectingOutputCapturingTestCase(unittest.TestCase):
    """TestCase that captures output to a StringIO object, without patching."""

    def setUp(self):
        """Create a StringIO object to make assertions about."""
        super().setUp()
        self.__out = io.StringIO()

    @property
    def out(self):
        """A StringIO object we make assertions about."""
        return self.__out

    def assertOutputWas(self, expected):
        """Assert the output has expected content, and clear it."""
        actual = self.out.getvalue()
        self.out.seek(0)
        self.out.truncate(0)
        self.assertEqual(actual, expected)


# FIXME: Finish writing these tests (if context.Announce is to be kept).
class TestAnnounce(_NonRedirectingOutputCapturingTestCase):
    """Tests for the Announce context manager."""

    def test_announces_single_completed_task(self):
        with context.Announce('A', out=self.out):
            with self.subTest(when='start'):
                self.assertOutputWas('Starting task A.\n')

        with self.subTest(when='finish'):
            self.assertOutputWas('Finished task A.\n')

    def test_announces_single_raising_task(self):
        with self.subTest('Exception should propagate.'):
            with self.assertRaises(_FakeError):
                with context.Announce('A', out=self.out):
                    with self.subTest(when='start'):
                        self.assertOutputWas('Starting task A.\n')
                    raise _FakeError

        with self.subTest(when='finish'):
            self.assertOutputWas('_FakeError raised in task A.\n')

    def test_announces_two_nested_completed_tasks(self):
        with context.Announce('A', out=self.out):
            with self.subTest(task='A', when='start'):
                self.assertOutputWas('Starting task A.\n')

            with context.Announce('B', out=self.out):
                with self.subTest(task='B', when='start'):
                    self.assertOutputWas('Starting task B.\n')

            with self.subTest(task='B', when='finish'):
                self.assertOutputWas('Finished task B.\n')

        with self.subTest(task='A', when='finish'):
            self.assertOutputWas('Finished task A.\n')

    def test_announces_two_nested_raising_tasks(self):
        with self.subTest('Exception should propagate.', scope='outer'):
            with self.assertRaises(_FakeError):
                with context.Announce('A', out=self.out):
                    with self.subTest(task='A', when='start'):
                        self.assertOutputWas('Starting task A.\n')

                    try:
                        with context.Announce('B', out=self.out):
                            with self.subTest(task='B', when='start'):
                                self.assertOutputWas('Starting task B.\n')
                            raise _FakeError
                    finally:
                        with self.subTest(task='B', when='finish'):
                            expected = '_FakeError raised in task B.\n'
                            self.assertOutputWas(expected)

        with self.subTest(task='A', when='finish'):
            self.assertOutputWas('_FakeError raised in task A.\n')

    @parameterized.expand([
        ('no error', False, 'Finished task A.\n'),
        ('with error', True, '_FakeError raised in task A.\n'),
    ])
    def test_if_out_is_none_stdout_is_used(self, _name, do_error, end_message):
        announce = context.Announce('A')
        old_stdout = sys.stdout
        out1 = io.StringIO()
        out2 = io.StringIO()
        sys.stdout = out1
        try:
            with announce:
                sys.stdout = out2
                if do_error:
                    raise _FakeError
        except _FakeError:
            pass
        finally:
            sys.stdout = old_stdout

        with self.subTest('__enter__'):
            self.assertEqual(out1.getvalue(), 'Starting task A.\n')
        with self.subTest('__exit__'):
            self.assertEqual(out2.getvalue(), end_message)

    def test_repr_shows_name_and_out_if_not_none(self):
        expected = (r"Announce\('A', "
                    r'out=<_?io\.StringIO object at 0x[0-9a-fA-F]+>\)')
        announce = context.Announce('A', out=self.out)
        self.assertRegex(repr(announce), expected)

    def test_repr_shows_just_name_if_out_is_none(self):
        announce = context.Announce('A')
        self.assertEqual(repr(announce), "Announce('A')")

    def test_name_attribute_has_name(self):
        announce = context.Announce('A', out=self.out)
        self.assertEqual(announce.name, 'A')

    def test_name_attribute_is_read_only(self):
        announce = context.Announce('A', out=self.out)
        with self.assertRaises(AttributeError):
            announce.name = 'B'

    def test_new_attributes_cannot_be_created(self):
        announce = context.Announce('A', out=self.out)
        with self.assertRaises(AttributeError):
            announce.blah = 'B'


class _NoClose:
    """
    Class without a close method, to help test context.Closing.

    Derived classes may or may not have a close method.
    """

    def __repr__(self):
        """Representation of this object as Python code."""
        return f'{type(self).__name__}()'

    def __str__(self):
        """Non-code representation. Tests that reprs are used where needed."""
        return f'{type(self).__name__} instance'


class _HasClose(_NoClose):
    """Class with a close method, to help test context.Closing."""

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class TestContextlibClosing(unittest.TestCase):
    """
    Tests for contextlib.closing, reused below to test context.Closing.

    We needn't test contextlib.closing, but writing the tests so those that
    apply to both are used to test both has the effect of testing the tests.
    Furthermore, in the future it is likely that we will have another "closing"
    implementation that will share most but not all tests with context.Closing.
    """

    @property
    def implementation(self):
        """The "closing" context manager implementation being tested."""
        return contextlib.closing

    def test_enter_returns_initializer_argument(self):
        obj = _HasClose()
        with self.implementation(obj) as ctx:
            self.assertIs(ctx, obj)

    def test_enter_does_not_close(self):
        obj = _HasClose()
        with self.implementation(obj):
            self.assertFalse(obj.closed)

    def test_exit_closes(self):
        obj = _HasClose()
        with self.implementation(obj):
            if obj.closed:
                raise Exception("can't check if __exit__ closes, already closed")
        self.assertTrue(obj.closed)

    def test_presence_of_close_is_not_pre_checked(self):
        got_to_exit = False
        try:
            with self.implementation(_NoClose()):
                got_to_exit = True
        except AttributeError:
            pass
        self.assertTrue(got_to_exit)

    def test_calling_close_attempted_even_if_absent(self):
        with self.subTest('AttributeError raised'):
            with self.assertRaises(AttributeError) as ctx:
                with self.implementation(_NoClose()):
                    pass

        with self.subTest('AttributeError name attribute'):
            self.assertEqual(ctx.exception.name, 'close')

    def test_exit_closes_even_if_close_was_just_patched_in(self):
        closed = False

        def just_in_time_close():
            nonlocal closed
            closed = True

        obj = _NoClose()
        with self.implementation(obj):
            obj.close = just_in_time_close

        self.assertTrue(closed)


class TestClosing(TestContextlibClosing):
    """Tests for the context.Closing class."""

    @property
    def implementation(self):
        return context.Closing

    def test_repr_shows_type_and_initializer_argument(self):
        cm = self.implementation(_HasClose())
        self.assertEqual(repr(cm), 'Closing(_HasClose())')


if __name__ == '__main__':
    unittest.main()
