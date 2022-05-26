#!/usr/bin/env python

"""Tests for gencomp1.py."""

import itertools
import sys

import pytest
from typeguard import typechecked

import gencomp1


@typechecked
class TestZipTwo:
    """Tests for the zip_two function."""

    __slots__ = ()

    def test_empty_iterables_zip_empty(self) -> None:
        """Zipping empty iterables yields no elements."""
        it = gencomp1.zip_two([], [])
        with pytest.raises(StopIteration):
            next(it)

    def test_nonempty_empty_zips_empty(self) -> None:
        """Zipping a nonempty iterable with an empty one yields no elements."""
        it = gencomp1.zip_two([10], [])
        with pytest.raises(StopIteration):
            next(it)

    def test_empty_nonempty_zips_empty(self) -> None:
        """Zipping an empty iterable with a nonempty one yields no elements."""
        it = gencomp1.zip_two([], [10])
        with pytest.raises(StopIteration):
            next(it)

    def test_shorter_longer_zips_shorter(self) -> None:
        """Zipping a shorter iterable with a longer one works correctly."""
        it = gencomp1.zip_two([10], [20, 30])
        assert list(it) == [(10, 20)]

    def test_longer_shorter_zips_shorter(self) -> None:
        """Zipping a longer iterable with a shorter one works correctly."""
        it = gencomp1.zip_two([10, 20], [30])
        assert list(it) == [(10, 30)]

    def test_equal_lengths_zip_all(self) -> None:
        """Zipping iterables with equally many of elements works correctly."""
        it = gencomp1.zip_two([10, 20, 30], ['foo', 'bar', 'baz'])
        assert list(it) == [(10, 'foo'), (20, 'bar'), (30, 'baz')]

    def test_finite_infinite_zips_finite(self) -> None:
        """Zipping a finite iterable with an infinite one works correctly."""
        it = gencomp1.zip_two([10, 20, 30], itertools.count(1))
        assert list(it) == [(10, 1), (20, 2), (30, 3)]

    def test_infinite_finite_zips_finite(self) -> None:
        """Zipping an infinite iterable with a finite one works correctly."""
        it = gencomp1.zip_two(itertools.count(1), [10, 20, 30])
        assert list(it) == [(1, 10), (2, 20), (3, 30)]


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
