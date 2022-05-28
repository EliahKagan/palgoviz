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
        """Clear the output buffer, asserting it had expected content."""
        actual = self.out.getvalue()
        self.out.seek(0)
        self.out.truncate(0)
        self.assertEqual(actual, expected)


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


if __name__ == '__main__':
    unittest.main()
