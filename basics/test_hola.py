#!/usr/bin/env python

"""Tests for hola.py."""

import io
import sys
import unittest

import hola


class HolaTest(unittest.TestCase):
    """Tests for hola.run."""

    __slots__ = ('_stdin', '_stdout', '_old_stdin', '_old_stdout')


    def setUp(self):
        """Redirect standard input and output."""
        self._stdin = io.StringIO('nombre')
        self._stdout = io.StringIO()
        self._old_stdin = sys.stdin
        self._old_stdout = sys.stdout
        sys.stdin = self._stdin
        sys.stdout = self._stdout

    def tearDown(self):
        """Undo standard input and output redirections."""
        sys.stdin = self._old_stdin
        sys.stdout = self._old_stdout

    # FIXME: This test is not specific enough. It should be split.
    #        If we mock the streams, we can split this into multiple tests.
    def test_output_is_correct(self):
        """The prompt is a question followed by a space and no newline."""
        hola.run()
        all_output = self._stdout.getvalue()
        self.assertEqual(all_output, '¿Como se llama usted? ¡Hola, nombre!\n')
