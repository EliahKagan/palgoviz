#!/usr/bin/env python

"""Tests for context managers in context.py."""

import io
import unittest

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


class TestClosing(unittest.TestCase):
    """Tests for the context.Closing class."""

    def test_repr_show_type_and_initializer_argument(self):
        cm = context.Closing(_HasClose())
        self.assertEqual(repr(cm), 'Closing(_HasClose())')

    def test_enter_returns_initializer_argument(self):
        obj = _HasClose()
        with context.Closing(obj) as ctx:
            self.assertIs(ctx, obj)

    def test_enter_does_not_close(self):
        obj = _HasClose()
        with context.Closing(obj):
            self.assertFalse(obj.closed)

    def test_exit_closes(self):
        obj = _HasClose()
        with context.Closing(obj):
            if obj.closed:
                raise Exception("can't check if __exit__ closes, already closed")
        self.assertTrue(obj.closed)

    def test_presence_of_close_is_not_pre_checked(self):
        got_to_exit = False
        try:
            with context.Closing(_NoClose()):
                got_to_exit = True
        except AttributeError:
            pass
        self.assertTrue(got_to_exit)

    def test_calling_close_attempted_even_if_absent(self):
        with self.subTest('AttributeError raised'):
            with self.assertRaises(AttributeError) as ctx:
                with context.Closing(_NoClose()):
                    pass

        with self.subTest('AttributeError name attribute'):
            self.assertEqual(ctx.exception.name, 'close')

    def test_exit_closes_even_if_close_was_just_patched_in(self):
        closed = False

        def just_in_time_close():
            nonlocal closed
            closed = True

        obj = _NoClose()
        with context.Closing(obj):
            obj.close = just_in_time_close

        self.assertTrue(closed)


if __name__ == '__main__':
    unittest.main()
