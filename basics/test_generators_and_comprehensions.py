#!/usr/bin/env python

"""Tests for generators_and_comprehensions.py."""

import itertools
import unittest

from generators_and_comprehensions import zip_two


class ZipTwoTest(unittest.TestCase):
    """Tests for generators_and_comprehensions.zip_two."""

    __slots__ = ()

    def empty_iterables_zip_empty(self):
        """Zipping empty iterables yields no elements."""
        it = zip_two([], [])
        with self.assertRaises(StopIteration):
            next(it)

    def nonempty_empty_zips_empty(self):
        """Zipping a nonempty iterable with an empty one yields no elements."""
        it = zip_two([10], [])
        with self.assertRaises(StopIteration):
            next(it)

    def empty_nonempty_zips_empty(self):
        """Zipping an empty iterable with a nonempty one yields no elements."""
        it = zip_two([], [10])
        with self.assertRaises(StopIteration):
            next(it)

    def shorter_longer_zips_shorter(self):
        """Zipping a shorter iterable with a longer one works correctly."""
        it = zip_two([10], [20, 30])
        self.assertSequenceEqual(list(it), [(10, 20)])

    def longer_shorter_zips_shorter(self):
        """Zipping a longer iterable with a shorter one works correctly."""
        it = zip_two([10, 20], [30])
        self.assertSequenceEqual(list(it), [(10, 20)])

    def equal_lengths_zip_all(self):
        """Zipping iterables with equally many of elements works correctly."""
        it = zip_two([10, 20, 30], ['foo', 'bar', 'baz'])
        self.assertSequenceEqual(list(it),
                                 [(10, 'foo'), (20, 'bar'), (30, 'baz')])

    def finite_infinite_zips_finite(self):
        """Zipping a finite iterable with an infinite one works correctly."""
        it = zip_two([10, 20, 30], itertools.count(1))
        self.assertSequenceEqual(list(it), [(10, 1), (20, 2), (30, 3)])

    def infinite_finite_zips_finite(self):
        """Zipping an infinite iterable with a finite one works correctly."""
        it = zip_two(itertools.count(1), [10, 20, 30])
        self.assertSequenceEqual(list(it), [(1, 10), (2, 20), (3, 30)])
