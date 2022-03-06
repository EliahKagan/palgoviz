#!/usr/bin/env python

"""Tests for functions in gencomp2.py."""

from collections.abc import Iterator
import itertools
import sys

import pytest

import gencomp2


@pytest.mark.parametrize('implementation', [
    itertools.product,
    gencomp2.product_two,
    gencomp2.product_two_alt,
])
class TestProductTwo:
    """Tests for product_two and product_two_alt."""

    __slots__ = ()

    def test_product_of_strings(self, implementation):
        """The Cartesian product of small nonempty strings is computed."""
        result = implementation('hi', 'bye')
        assert isinstance(result, Iterator)
        assert list(result) == [
            ('h', 'b'), ('h', 'y'), ('h', 'e'),
            ('i', 'b'), ('i', 'y'), ('i', 'e'),
        ]

    def test_empty_with_nonempty_is_empty(self, implementation):
        """The Cartesian product of empty and nonempty ranges is empty."""
        result = implementation(range(0), range(2))
        with pytest.raises(StopIteration):
            next(result)

    def test_nonempty_with_empty_is_empty(self, implementation):
        """The Cartesian product of nonempty and empty ranges is empty."""
        result = implementation(range(2), range(0))
        with pytest.raises(StopIteration):
            next(result)

    def test_product_of_generators(self, implementation):
        """The Cartesian product of small nonempty generators is computed."""
        result = implementation((x - 1 for x in (1, 2)),
                                (x + 5 for x in (3, 4)))
        assert isinstance(result, Iterator)
        assert list(result) == [(0, 8), (0, 9), (1, 8), (1, 9)]


@pytest.mark.parametrize('implementation', [
    gencomp2.ascending_countdowns,
    gencomp2.ascending_countdowns_alt,
])
class TestAscendingCountdowns:
    """Tests for ascending_countdowns and ascending_countdowns_alt."""

    __slots__ = ()

    def test_first_25_correct(self, implementation):
        """The first 25 elements have the correct values."""
        result = implementation()
        assert isinstance(result, Iterator)
        assert list(itertools.islice(result, 25)) == [
            0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 6,
            5, 4, 3
        ]

    def test_first_million_have_correct_sum(self, implementation):
        """The first million elements have the same sum as correct values."""
        result = implementation()
        assert isinstance(result, Iterator)
        assert sum(itertools.islice(result, 1_000_000)) == 471_108_945


@pytest.mark.parametrize('implementation', [
    gencomp2.three_sums,
    gencomp2.three_sums_alt,
])
class TestThreeSums:
    """Tests for three_sums and three_sums_alt."""

    __slots__ = ()

    def test_impossible_choice_gives_no_sums(self, implementation):
        """When an input iterable is empty, there are no sums."""
        assert implementation([2, 3], [], [20, 30]) == set()

    def test_finds_sums_from_small_nontrivial_example(self, implementation):
        """A small example including iterators produces all possible sums."""
        a = (n * 10 for n in (1, 2, 3))
        b = [7, 7, 14]
        c = iter(range(2, 5))

        assert implementation(a, b, c) == {
            19, 20, 21, 26, 27, 28, 29, 30, 31, 36, 37, 38, 39, 40, 41, 46, 47,
            48
        }

    def test_finds_sums_from_three_identical_ranges(self, implementation):
        """All sums of elements from three small identical ranges are found."""
        result = implementation(range(10), range(10), range(10))
        assert result == set(range(28))


@pytest.mark.parametrize('implementation', [
    gencomp2.three_sum_indices_1,
    gencomp2.three_sum_indices_2,
    gencomp2.three_sum_indices_3,
    gencomp2.three_sum_indices_4,
])
class TestThreeSumIndices:
    """Tests for the four three_sum_indices functions."""

    __slots__ = ()

    def test_finds_indices_in_small_nontrivial_example(self, implementation):
        """A small example with small tuples and target is solved correctly."""
        result = implementation([1, 2, 3], [10, 9], [7, 9, 8], 20)
        assert isinstance(result, Iterator)
        assert list(result) == [(0, 0, 1), (1, 0, 2), (2, 0, 0), (2, 1, 2)]

    def test_all_equal_values_have_no_eligible_sums(self, implementation):
        """When all values are the same, no distinct-addends sum exists."""
        result = implementation([0] * 10, [0] * 20, [0] * 30, 0)
        with pytest.raises(StopIteration):
            next(result)

    def test_when_all_combinations_work_all_are_found(self, implementation):
        """When input is "stacked" so all sums win, the are all reported."""
        a = itertools.repeat(1, 10)
        b = itertools.repeat(2, 20)
        c = itertools.repeat(3, 30)

        result = implementation(a, b, c, 6)
        assert isinstance(result, Iterator)

        listed = list(result)
        assert len(listed) == 6000  # Correct length.

        expected = list(itertools.product(range(10), range(20), range(30)))
        assert listed == expected  # Correct values in the correct order.


class TestDotProduct:
    """Tests for the dot_product function."""

    __slots__ = ()

    def test_4_entries_dot_2_entries(self):
        """Simple test: dot product of vectors of support 4 and 2."""
        u = {'a': 2, 'b': 3, 'c': 4, 'd': 5}
        v = {'b': 0.5, 'd': 1}
        assert gencomp2.dot_product(u, v) == 6.5

    def test_2_entries_dot_4_entries(self):
        """Simple test: dot product of vectors of support 2 and 4."""
        u = {'a': 2, 'b': 3, 'c': 4, 'd': 5}
        v = {'b': 0.5, 'd': 1}
        assert gencomp2.dot_product(v, u) == 6.5

    def test_partially_overlapping_1(self):
        """Dot product of dicts whose keys partly overlap (1/3)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        assert round(gencomp2.dot_product(u, v), 2) == 21.56

    def test_partially_overlapping_2(self):
        """Dot product of dicts whose keys partly overlap (2/3: reversed)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        assert round(gencomp2.dot_product(v, u), 2) == 21.56

    def test_partially_overlapping_3(self):
        """Dot product of dicts whose keys partly overlap (3/3: symmetry)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        uv = gencomp2.dot_product(u, v)
        vu = gencomp2.dot_product(v, u)
        assert uv == vu

    def test_single_key_overlapping_1(self):
        """Dot product of dicts that share only one key (1/2)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert gencomp2.dot_product(u, w) == 4.5

    def test_single_key_overlapping_2(self):
        """Dot product of dicts that share only one key (2/2: reversed)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert gencomp2.dot_product(w, u) == 4.5

    def test_no_keys_overlapping_is_zero_1(self):
        """The dot product of dicts with disjoint keys is 0 (1/2)."""
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert gencomp2.dot_product(v, w) == 0

    def test_no_keys_overlapping_is_zero_2(self):
        """The dot product of dicts with disjoint keys is 0 (2/2: reversed)."""
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert gencomp2.dot_product(w, v) == 0


class TestFlatten2:
    """Tests for the flatten2 function."""

    __slots__ = ()

    def test_mixed_depths_flatten_by_exactly_two(self):
        """An nested sequence of assorted depths flattens properly."""
        iterable = [0, [1, 2], (3, 4, [5, 6, [7]], 8), [9], 10, [{(11,)}]]
        result = gencomp2.flatten2(iterable)
        assert isinstance(result, Iterator)
        assert list(result) == [5, 6, [7], (11,)]

    def too_shallow_collection_flattens_empty(self):
        """When there are no sub-sub-elements, nothing is yielded."""
        iterable = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        result = gencomp2.flatten2(iterable)
        with pytest.raises(StopIteration):
            next(result)

    def test_same_depth_str(self):
        """Flattening a simple nested list of strings gives the characters."""
        iterable = [['foo', 'bar', 'baz'], ['ham', 'spam', 'eggs']]
        result = gencomp2.flatten2(iterable)
        assert isinstance(result, Iterator)
        assert list(result) == list('foobarbazhamspameggs')

    def test_repeated_sequence_in_input_gives_repeated_output(self):
        """If the same sequence is encountered twice, it's processed twice."""
        iterable = ['hi', [range(5)] * 3, 'bye']
        result = gencomp2.flatten2(iterable)
        assert isinstance(result, Iterator)
        assert list(result) == [
            'h', 'i',
            0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4,
            'b', 'y', 'e',
        ]

    def test_repeated_iterator_in_input_does_not_repeat_in_output(self):
        """
        If the same iterator is encountered twice, the first time exhausts it.

        This is the behavior one automatically gets if one does not specially
        handle the situation. It is also the intended behavior.
        """
        iterable = ['hi', [iter(range(5))] * 3, 'bye']
        result = gencomp2.flatten2(iterable)
        assert isinstance(result, Iterator)
        assert list(result) == ['h', 'i', 0, 1, 2, 3, 4, 'b', 'y', 'e']

    def test_strings_are_never_too_shallow(self):
        """Since str is an iterable of str, excess flattening is idempotent."""
        iterable = 'turtles'  # It's turtles all the way down.
        result = gencomp2.flatten2(iterable)
        assert isinstance(result, Iterator)
        assert list(result) == ['t', 'u', 'r', 't', 'l', 'e', 's']


class TestUngroup:
    """Tests for the ungroup function."""

    __slots__ = ()

    def test_empty_graph(self):
        """A graph with no vertices or edges is found to have no edges."""
        assert gencomp2.ungroup({}) == set()

    def test_totally_disconnected_graph(adj):
        """A graph with vertices but no edges is found to have no edges."""
        adj = {'a': [], 'b': [], 'c': [], 'd': [], 'e': [], 'f': [], 'g': []}

    def test_sparse_graph(self):
        """Testing a sparse graph, some of whose vertices are isolated."""
        adj = {
            1: [2, 3], 2: [4, 5], 3: [6, 7], 4: [8, 9],
            5: [], 6: [], 7: [], 8: [], 9: [2, 5],
        }

        assert gencomp2.ungroup(adj) == {
            (1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7),
            (4, 8), (4, 9), (9, 2), (9, 5),
        }

    def test_medium_density_graph(self):
        """Testing a graph with about half as many edges as it can support."""
        adj = {'a': ['b', 'c', 'd'], 'b': ['a', 'd'], 'c': ['a', 'd'], 'd': []}

        assert gencomp2.ungroup(adj) == {
            ('a', 'b'), ('a', 'c'), ('a', 'd'),
            ('b', 'a'), ('b', 'd'), ('c', 'a'), ('c', 'd'),
        }

    def test_complete_graph(self):
        """A graph with all possible edges is found to have all of them."""
        adj = {
            'a': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'b': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'c': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'd': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'e': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'f': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'g': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            'h': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
        }

        assert gencomp2.ungroup(adj) == {
            ('a', 'a'), ('a', 'b'), ('a', 'c'), ('a', 'd'), ('a', 'e'),
            ('a', 'f'), ('a', 'g'), ('a', 'h'), ('b', 'a'), ('b', 'b'),
            ('b', 'c'), ('b', 'd'), ('b', 'e'), ('b', 'f'), ('b', 'g'),
            ('b', 'h'), ('c', 'a'), ('c', 'b'), ('c', 'c'), ('c', 'd'),
            ('c', 'e'), ('c', 'f'), ('c', 'g'), ('c', 'h'), ('d', 'a'),
            ('d', 'b'), ('d', 'c'), ('d', 'd'), ('d', 'e'), ('d', 'f'),
            ('d', 'g'), ('d', 'h'), ('e', 'a'), ('e', 'b'), ('e', 'c'),
            ('e', 'd'), ('e', 'e'), ('e', 'f'), ('e', 'g'), ('e', 'h'),
            ('f', 'a'), ('f', 'b'), ('f', 'c'), ('f', 'd'), ('f', 'e'),
            ('f', 'f'), ('f', 'g'), ('f', 'h'), ('g', 'a'), ('g', 'b'),
            ('g', 'c'), ('g', 'd'), ('g', 'e'), ('g', 'f'), ('g', 'g'),
            ('g', 'h'), ('h', 'a'), ('h', 'b'), ('h', 'c'), ('h', 'd'),
            ('h', 'e'), ('h', 'f'), ('h', 'g'), ('h', 'h'),
        }


class TestMakeMulTable:
    """Tests for the make_mul_table function."""

    __slots__ = ()

    def test_zero_times_zero_is_zero(self):
        """A one cell table, for (0, 0), shows that 0 * 0 == 0."""
        assert gencomp2.make_mul_table(0, 0) == [[0]]

    def test_small_landscape_table(self):
        """A small table with one more column than rows has correct values."""
        assert gencomp2.make_mul_table(3, 4) == [
            [0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4],
            [0, 2, 4, 6, 8],
            [0, 3, 6, 9, 12],
        ]

    def test_small_portrait_table(self):
        """A small table with one more row than columns has correct values."""
        assert gencomp2.make_mul_table(4, 3) == [
            [0, 0, 0, 0],
            [0, 1, 2, 3],
            [0, 2, 4, 6],
            [0, 3, 6, 9],
            [0, 4, 8, 12],
        ]

    def test_ordinary_sized_table(self):
        """A table for 0 times 0 up to 10 times 10 has correct values."""
        assert gencomp2.make_mul_table(10, 10) == [
            [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,   0],
            [0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  10],
            [0,  2,  4,  6,  8, 10, 12, 14, 16, 18,  20],
            [0,  3,  6,  9, 12, 15, 18, 21, 24, 27,  30],
            [0,  4,  8, 12, 16, 20, 24, 28, 32, 36,  40],
            [0,  5, 10, 15, 20, 25, 30, 35, 40, 45,  50],
            [0,  6, 12, 18, 24, 30, 36, 42, 48, 54,  60],
            [0,  7, 14, 21, 28, 35, 42, 49, 56, 63,  70],
            [0,  8, 16, 24, 32, 40, 48, 56, 64, 72,  80],
            [0,  9, 18, 27, 36, 45, 54, 63, 72, 81,  90],
            [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        ]


if __name__ == '__main__':
    sys.exit(pytest.main())
