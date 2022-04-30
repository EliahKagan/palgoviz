#!/usr/bin/env python

"""Tests for functions in gencomp2.py."""

from collections.abc import Iterator
import itertools
import sys

import pytest

import gencomp2


@pytest.mark.parametrize('implementation', [
    itertools.product,  # Included to help test that the tests are correct.
    gencomp2.product_two,
    gencomp2.product_two_alt,
    gencomp2.product_two_flexible,
    gencomp2.my_product,
    gencomp2.my_product_slow,
])
class TestProductTwo:
    """
    Shared tests for all Cartesian product functions in gencomp2.

    These tests test only the Cartesian product of two iterables (binary
    Cartesian products), even when the code under test is not restricted to
    that. For that reason, these are all the tests for product_two and
    product_two_alt, but the others have further tests below.
    """

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


class TestProductTwoFlexible:
    """Tests specific to product_two_flexible."""

    __slots__ = ()

    def test_product_of_infinite_iterator_and_sequence(self):
        """
        A Cartesian product with an infinite first argument generates values.

        This tests the "flexible" logic where the first argument is not
        materialized.
        """
        result = gencomp2.product_two_flexible(itertools.count(), 'abc')
        assert isinstance(result, Iterator)
        prefix = itertools.islice(result, 7)
        assert list(prefix) == [
            (0, 'a'), (0, 'b'), (0, 'c'),
            (1, 'a'), (1, 'b'), (1, 'c'),
            (2, 'a')
        ]

    def test_product_of_infinite_and_finite_iterators(self):
        """
        A Cartesian product with an infinite first argument reuses other
        arguments.

        This tests that, in the "flexible" logic where the first argument is
        not materialized, other arguments are still materialized.
        """
        result = gencomp2.product_two_flexible(itertools.count(),
                                               (ch for ch in 'abc'))
        assert isinstance(result, Iterator)
        prefix = itertools.islice(result, 7)
        assert list(prefix) == [
            (0, 'a'), (0, 'b'), (0, 'c'),
            (1, 'a'), (1, 'b'), (1, 'c'),
            (2, 'a')
        ]


@pytest.mark.parametrize('implementation', [
    itertools.product,  # Included to help test that the tests are correct.
    gencomp2.my_product,
    gencomp2.my_product_slow,
])
class TestMyProductSlow:
    """Tests specific to, and shared by, my_product and my_product_slow."""

    __slots__ = ()

    def test_product_of_sequences(self, implementation):
        """A Cartesian product of several short sequences is computed."""
        result = implementation('ab', 'cde', 'fg', 'hi')
        assert isinstance(result, Iterator)
        assert list(result) == [
            ('a', 'c', 'f', 'h'), ('a', 'c', 'f', 'i'), ('a', 'c', 'g', 'h'),
            ('a', 'c', 'g', 'i'), ('a', 'd', 'f', 'h'), ('a', 'd', 'f', 'i'),
            ('a', 'd', 'g', 'h'), ('a', 'd', 'g', 'i'), ('a', 'e', 'f', 'h'),
            ('a', 'e', 'f', 'i'), ('a', 'e', 'g', 'h'), ('a', 'e', 'g', 'i'),
            ('b', 'c', 'f', 'h'), ('b', 'c', 'f', 'i'), ('b', 'c', 'g', 'h'),
            ('b', 'c', 'g', 'i'), ('b', 'd', 'f', 'h'), ('b', 'd', 'f', 'i'),
            ('b', 'd', 'g', 'h'), ('b', 'd', 'g', 'i'), ('b', 'e', 'f', 'h'),
            ('b', 'e', 'f', 'i'), ('b', 'e', 'g', 'h'), ('b', 'e', 'g', 'i'),
        ]

    def test_product_of_sequences_and_iterators(self, implementation):
        """
        A Cartesian product of a mix of sequences and iterators is computed.
        """
        result = implementation(iter('ab'), 'cde', iter('fg'), 'hi')
        assert isinstance(result, Iterator)
        assert list(result) == [
            ('a', 'c', 'f', 'h'), ('a', 'c', 'f', 'i'), ('a', 'c', 'g', 'h'),
            ('a', 'c', 'g', 'i'), ('a', 'd', 'f', 'h'), ('a', 'd', 'f', 'i'),
            ('a', 'd', 'g', 'h'), ('a', 'd', 'g', 'i'), ('a', 'e', 'f', 'h'),
            ('a', 'e', 'f', 'i'), ('a', 'e', 'g', 'h'), ('a', 'e', 'g', 'i'),
            ('b', 'c', 'f', 'h'), ('b', 'c', 'f', 'i'), ('b', 'c', 'g', 'h'),
            ('b', 'c', 'g', 'i'), ('b', 'd', 'f', 'h'), ('b', 'd', 'f', 'i'),
            ('b', 'd', 'g', 'h'), ('b', 'd', 'g', 'i'), ('b', 'e', 'f', 'h'),
            ('b', 'e', 'f', 'i'), ('b', 'e', 'g', 'h'), ('b', 'e', 'g', 'i'),
        ]

    def test_long_product_of_pairs(self, implementation):
        """
        The first 10,000 of a 2**90-element Cartesian product sum correctly.
        """
        arguments = [(0, 1)] * 90
        result = implementation(*arguments)
        assert isinstance(result, Iterator)

        prefix = itertools.islice(result, 10_000)
        flattened_prefix_sum = sum(map(sum, prefix))
        assert flattened_prefix_sum == 64_608


class TestMyProduct:
    """A test specific to my_product."""

    __slots__ = ()

    def test_long_product_of_pairs_seems_efficient(self):
        """
        The first 10,000 of a 2**900-element Cartesian product sum correctly.
        """
        arguments = [(0, 1)] * 90
        result = gencomp2.my_product(*arguments)
        assert isinstance(result, Iterator)

        prefix = itertools.islice(result, 10_000)
        flattened_prefix_sum = sum(map(sum, prefix))
        assert flattened_prefix_sum == 64_608


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
        """When input is "stacked" so all sums win, they are all reported."""
        a = itertools.repeat(1, 10)
        b = itertools.repeat(2, 20)
        c = itertools.repeat(3, 30)

        result = implementation(a, b, c, 6)
        assert isinstance(result, Iterator)

        listed = list(result)
        assert len(listed) == 6000, 'The length is correct.'

        expected = list(itertools.product(range(10), range(20), range(30)))
        assert listed == expected, 'Values are correct and correctly ordered.'


@pytest.mark.parametrize('implementation', [
    gencomp2.dot_product_slow,
    gencomp2.dot_product,
])
class TestDotProduct:
    """Tests for the dot_product_slow and dot_product functions."""

    __slots__ = ()

    def test_4_entries_dot_2_entries(self, implementation):
        """Simple test: dot product of vectors of support 4 and 2."""
        u = {'a': 2, 'b': 3, 'c': 4, 'd': 5}
        v = {'b': 0.5, 'd': 1}
        assert implementation(u, v) == 6.5

    def test_2_entries_dot_4_entries(self, implementation):
        """Simple test: dot product of vectors of support 2 and 4."""
        u = {'a': 2, 'b': 3, 'c': 4, 'd': 5}
        v = {'b': 0.5, 'd': 1}
        assert implementation(v, u) == 6.5

    def test_partially_overlapping_1(self, implementation):
        """Dot product of dicts whose keys partly overlap (1/3)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        assert round(implementation(u, v), 2) == 21.56

    def test_partially_overlapping_2(self, implementation):
        """Dot product of dicts whose keys partly overlap (2/3: reversed)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        assert round(implementation(v, u), 2) == 21.56

    def test_partially_overlapping_3(self, implementation):
        """Dot product of dicts whose keys partly overlap (3/3: symmetry)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        uv = implementation(u, v)
        vu = implementation(v, u)
        assert uv == vu

    def test_single_key_overlapping_1(self, implementation):
        """Dot product of dicts that share only one key (1/2)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert implementation(u, w) == 4.5

    def test_single_key_overlapping_2(self, implementation):
        """Dot product of dicts that share only one key (2/2: reversed)."""
        u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert implementation(w, u) == 4.5

    def test_no_keys_overlapping_is_zero_1(self, implementation):
        """The dot product of dicts with disjoint keys is 0 (1/2)."""
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert implementation(v, w) == 0

    def test_no_keys_overlapping_is_zero_2(self, implementation):
        """The dot product of dicts with disjoint keys is 0 (2/2: reversed)."""
        v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
        w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
        assert implementation(w, v) == 0


class TestFlatten2:
    """Tests for the flatten2 function."""

    __slots__ = ()

    def test_mixed_depths_flatten_by_exactly_two(self):
        """An nested sequence of assorted depths flattens properly."""
        iterable = [0, [1, 2], (3, 4, [5, 6, [7]], 8), [9], 10, [{(11,)}]]
        result = gencomp2.flatten2(iterable)
        assert isinstance(result, Iterator)
        assert list(result) == [5, 6, [7], (11,)]

    def test_too_shallow_collection_flattens_empty(self):
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


@pytest.fixture(name='status_colors')
def fixture_status_colors():
    """Some made up "status" colors for testing dict composing functions."""
    return dict(unspecified='gray', OK='green', meh='blue',
                concern='yellow', alarm='orange', danger='red')


@pytest.fixture(name='color_rgbs')
def fixture_color_rgbs():
    """Some colors' RGB hex values, for testing dict composing functions."""
    return dict(violet=0xEE82EE, red=0xFF0000, gray=0x808080,
                black=0x000000, green=0x008000, orange=0xFFA500,
                azure=0xF0FFFF, yellow=0xFFFF00, blue=0x0000FF)


@pytest.mark.parametrize('implementation', [
    gencomp2.compose_dicts_simple,
    gencomp2.compose_dicts,
])
class TestComposeDictsSimpleAndComposeDicts:
    """
    Shared tests for the compose_dicts_simple and compose_dicts functions.
    """

    __slots__ = ()

    def test_composition_of_empty_dicts_is_empty(self, implementation):
        """An empty dict composed with an empty dict is an empty dict."""
        assert implementation({}, {}) == {}

    def test_no_loss_when_back_has_all_front_values(self, implementation,
                                                    status_colors, color_rgbs):
        """When all values of front are keys of back, nothing is dropped."""
        status_rgbs = implementation(color_rgbs, status_colors)

        assert status_rgbs == {
            'unspecified': 0x808080, 'OK': 0x008000, 'meh': 0x0000FF,
            'concern': 0xFFFF00, 'alarm': 0xFFA500, 'danger': 0xFF0000,
        }

    def test_order_is_preserved_when_back_is_total(self, implementation,
                                                   status_colors, color_rgbs):
        """When all keys of front map through, results are in that order."""
        status_rgbs = implementation(color_rgbs, status_colors)

        assert list(status_rgbs.items()) == [
            ('unspecified', 0x808080), ('OK', 0x008000), ('meh', 0x0000FF),
            ('concern', 0xFFFF00), ('alarm', 0xFFA500), ('danger', 0xFF0000),
        ]

    def test_all_lost_when_back_has_no_front_values(self, implementation,
                                                    status_colors, color_rgbs):
        """When no values of front are keys of back, everything is dropped."""
        wrong_order_composition = implementation(status_colors, color_rgbs)
        assert wrong_order_composition == {}

    def test_self_composition_works_even_with_some_loss(self, implementation):
        """"Squaring" a dict whose keys and values partly overlap works."""
        squares = {x: x**2 for x in range(1, 100)}
        result = implementation(squares, squares)
        assert result == {
            1: 1, 2: 16, 3: 81, 4: 256, 5: 625, 6: 1296, 7: 2401, 8: 4096,
            9: 6561,
        }

    def test_self_composition_preserves_key_order(self, implementation):
        """"Squaring" a dict is stable with respect to key iteration order."""
        squares = {x: x**2 for x in range(1, 100)}
        result = implementation(squares, squares)
        assert list(result.items()) == [
            (1, 1), (2, 16), (3, 81), (4, 256), (5, 625), (6, 1296), (7, 2401),
            (8, 4096), (9, 6561),
        ]

    def test_back_values_do_not_need_to_be_hashable(self, implementation):
        """The back dict's values aren't used as keys so they need not hash."""
        d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
        d2 = {('b', 'c'): 30, None: 20, 'a': 40}
        result = implementation(d1, d2)
        assert result == {('b', 'c'): ['d', 'e'], None: ('b', 'c'), 'a': None}

    def test_non_hashable_back_values_do_not_harm_order(self, implementation):
        """Composition stability is unaffected by hashability of outputs."""
        d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
        d2 = {('b', 'c'): 30, None: 20, 'a': 40}
        result = implementation(d1, d2)
        assert list(result.items()) == [
            (('b', 'c'), ['d', 'e']), (None, ('b', 'c')), ('a', None),
        ]

    def test_back_value_hashability_need_not_be_obvious(self, implementation):
        """The back dict's values can nonhashable objects of hashable type."""
        back = {42: (set(),)}
        front = {'foo': 42}
        assert implementation(back, front) == {'foo': (set(),)}


class TestComposeDictsSimple:
    """A test specific to the compose_dicts_simple function."""

    __slots__ = ()

    def test_front_values_must_be_hashable(self):
        """If any value of front is not hashable, TypeError is raised."""
        d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
        d2 = {('b', 'c'): 30, None: 20, 'a': 40}

        with pytest.raises(TypeError) as exc_info:
            gencomp2.compose_dicts_simple(d2, d1)

        assert exc_info.exconly() == "TypeError: unhashable type: 'list'"

    def test_front_values_must_really_be_hashable_objects(self):
        """Even non-hashable front values of hashable type raise TypeError."""
        back = {}
        front = {42: (set(),)}

        with pytest.raises(TypeError) as exc_info:
            gencomp2.compose_dicts_simple(back, front)

        assert exc_info.exconly() == "TypeError: unhashable type: 'set'"


class TestComposeDicts:
    """Tests specific to the compose_dicts function."""

    __slots__ = ()

    def test_front_values_need_not_be_hashable(self):
        """If any value of front is not hashable, it goes silently unused."""
        d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
        d2 = {('b', 'c'): 30, None: 20, 'a': 40}
        result = gencomp2.compose_dicts(d2, d1)
        assert result == {10: 40, 20: 30, 40: 20}

    def test_non_hashable_front_values_do_not_harm_order(self):
        """Composition stability is unaffected by non-hashable front values."""
        d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
        d2 = {('b', 'c'): 30, None: 20, 'a': 40}
        result = gencomp2.compose_dicts(d2, d1)
        assert list(result.items()) == [(10, 40), (20, 30), (40, 20)]

    def test_front_values_can_be_unhashable_objects_of_hashable_type(self):
        """Unhashable front values are skipped even when of hashable type."""
        back = {}
        front = {42: (set(),)}
        assert gencomp2.compose_dicts(back, front) == {}

    def test_unhashable_front_values_of_hashable_type_do_not_harm_order(self):
        """
        Composition stability is unaffected by non-hashable front values even
        when of hashable type.
        """
        back = {
            'forty-one': [4, 1], 'forty-three': [4, 3], 'forty-two': [4, 2],
        }
        front = {43: 'forty-three', 42: (set(),), 41: 'forty-one'}
        result =  gencomp2.compose_dicts(back, front)
        assert list(result.items()) == [(43, [4, 3]), (41, [4, 1])]


class TestComposeDictsView:
    """Tests for the compose_dicts_view function."""

    __slots__ = ()

    def test_all_entries_are_present(self, color_rgbs, status_colors):
        """When all values of front are keys of back, front keys are mapped."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)

        assert get_rgb('unspecified') == 0x808080
        assert get_rgb('OK') == 0x008000
        assert get_rgb('meh') == 0x0000FF
        assert get_rgb('concern') == 0xFFFF00
        assert get_rgb('alarm') == 0xFFA500
        assert get_rgb('danger') == 0xFF0000

    def test_mappings_change_in_real_time(self, color_rgbs, status_colors):
        """Current values are returned before and after dict modification."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)
        assert get_rgb('OK') == 0x008000, 'Correct value before the change.'

        status_colors['OK'] = 'azure'
        assert get_rgb('OK') == 0xF0FFFF, 'Correct value after the change.'

    def test_broken_mappings_go_missing(self, color_rgbs, status_colors):
        """After a change breaks a mapping, accessing it raises KeyError."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)

        assert get_rgb('danger') == 0xFF0000, \
               'Correct value before the change.'

        status_colors['danger'] = 'vermillion'

        with pytest.raises(KeyError) as exc_info:
            get_rgb('danger')

        assert exc_info.exconly() == "KeyError: 'vermillion'", \
               'The intermediate key is reported not present after the change.'

        status_colors['danger'] = 'red'

        assert get_rgb('danger') == 0xFF0000, \
               'Correct value after rolling back the change.'

    def test_broken_mappings_ok_if_unused(self, color_rgbs, status_colors):
        """After a change breaks a mapping, unrelated mappings still work."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)
        status_colors['danger'] = 'vermillion'
        assert get_rgb('meh') == 0x0000FF

    def test_unhashable_mappings_fail_to_map(self, color_rgbs, status_colors):
        """Lookups using a newly unhashable front value raise TypeError."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)

        assert get_rgb('danger') == 0xFF0000, \
               'Correct value before the change.'

        status_colors['danger'] = [227, 66, 52]  # RGB values for vermillion.

        with pytest.raises(TypeError) as exc_info:
            get_rgb('danger')

        assert exc_info.exconly() == "TypeError: unhashable type: 'list'"

        status_colors['danger'] = 'red'

        assert get_rgb('danger') == 0xFF0000, \
               'Correct value after rolling back the change.'

    def test_unhashable_mappings_ok_if_unused(self, color_rgbs, status_colors):
        """Unhashable front values don't break unrelated lookups."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)
        status_colors['danger'] = [227, 66, 52]  # RGB values for vermillion.
        assert get_rgb('meh') == 0x0000FF

    def test_unhashable_objects_of_hashable_type_fail_to_map(self,
                                                             color_rgbs,
                                                             status_colors):
        """
        Lookups using a newly unhashable front value whose type is hashable
        raise TypeError.
        """
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)

        assert get_rgb('danger') == 0xFF0000, \
               'Correct value before the change.'

        # isinstance(tuple, Hashable), but this tuple object is not hashable.
        status_colors['danger'] = (set(),)

        with pytest.raises(TypeError) as exc_info:
            get_rgb('danger')

        assert exc_info.exconly() == "TypeError: unhashable type: 'set'"

        status_colors['danger'] = 'red'

        assert get_rgb('danger') == 0xFF0000, \
               'Correct value after rolling back the change.'

    def test_unhashable_mappings_ok_if_unused(self, color_rgbs, status_colors):
        """Unhashable front values don't break unrelated lookups."""
        get_rgb = gencomp2.compose_dicts_view(color_rgbs, status_colors)

        # isinstance(tuple, Hashable), but this tuple object is not hashable.
        status_colors['danger'] = (set(),)

        assert get_rgb('meh') == 0x0000FF


@pytest.fixture(name='make_matrix_indexer')
def fixture_make_matrix_indexer():
    """Make a factory of binary functions that 1-based index nested tuples."""
    return lambda nested_tuple: lambda i, j: nested_tuple[i - 1][j - 1]


class TestMatrixSquareFlat:
    """Tests for the matrix_square_flat function."""

    __slots__ = ()

    def test_empty_matrix_squares_empty(self, make_matrix_indexer):
        """With a matrix size n=0, the result is an empty dictionary."""
        f = make_matrix_indexer(())
        n = 0
        assert gencomp2.matrix_square_flat(f, n) == {}

    def test_1_by_1_matrix_squares_as_scalar(self, make_matrix_indexer):
        """The square of a 1-by-1 matrix is a 1-by-1 matrix of the square."""
        matrix = ((3,),)
        f = make_matrix_indexer(matrix)
        n = 1
        assert gencomp2.matrix_square_flat(f, n) == {(1, 1): 9}

    def test_2_by_2_matrix(self, make_matrix_indexer):
        """Squaring a 2x2 matrix representing i gives one representing -1."""
        matrix = ((0, -1), (-1, 0))
        f = make_matrix_indexer(matrix)
        n = 2
        assert gencomp2.matrix_square_flat(f, n) == {
            (1, 1): 1, (1, 2): 0,
            (2, 1): 0, (2, 2): 1,
        }

    def test_3_by_3_matrix(self, make_matrix_indexer):
        """Squaring a 3x3 matrix produces the correct result."""
        matrix = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        f = make_matrix_indexer(matrix)
        n = 3
        assert gencomp2.matrix_square_flat(f, n) == {
            (1, 1):  30, (1, 2):  36, (1, 3):  42,
            (2, 1):  66, (2, 2):  81, (2, 3):  96,
            (3, 1): 102, (3, 2): 126, (3, 3): 150,
        }


class TestMatrixSquareNested:
    """Tests for the matrix_square_nested function."""

    __slots__ = ()

    def test_empty_matrix_squares_empty(self, make_matrix_indexer):
        """With a matrix size n=0, the result is an empty dictionary."""
        f = make_matrix_indexer(())
        n = 0
        assert gencomp2.matrix_square_nested(f, n) == []

    def test_1_by_1_matrix_squares_as_scalar(self, make_matrix_indexer):
        """The square of a 1-by-1 matrix is a 1-by-1 matrix of the square."""
        matrix = ((3,),)
        f = make_matrix_indexer(matrix)
        n = 1
        assert gencomp2.matrix_square_nested(f, n) == [[9]]

    def test_2_by_2_matrix(self, make_matrix_indexer):
        """Squaring a 2x2 matrix representing i gives one representing -1."""
        matrix = ((0, -1), (-1, 0))
        f = make_matrix_indexer(matrix)
        n = 2
        assert gencomp2.matrix_square_nested(f, n) == [[1, 0], [0, 1]]

    def test_3_by_3_matrix(self, make_matrix_indexer):
        """Squaring a 3x3 matrix produces the correct result."""
        matrix = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        f = make_matrix_indexer(matrix)
        n = 3
        result = gencomp2.matrix_square_nested(f, n)
        assert result == [[30, 36, 42], [66, 81, 96], [102, 126, 150]]


@pytest.mark.parametrize('implementation', [
    gencomp2.transpose,
    gencomp2.transpose_alt,
])
class TestTranspose:
    """Tests for transpose and transpose_alt."""

    __slots__ = ()

    def test_empty_matrix_transposes_empty(self, implementation):
        """With a 0x0 matrix, the result is also a 0x0 matrix."""
        matrix = ()
        assert implementation(matrix) == ()

    def test_1_by_1_matrix_transposes_equal(self, implementation):
        """With a 1x1 matrix, the result is an equal matrix."""
        matrix = ((3,),)
        assert implementation(matrix) == ((3,),)

    def test_2_by_2_matrix(self, implementation):
        """Transposing a 2x2 matrix produces the correct 2x2 result."""
        matrix = ((1, 2), (3, 4))
        assert implementation(matrix) == ((1, 3), (2, 4))

    def test_3_by_3_matrix(self, implementation):
        """Transposing a 3x3 matrix produces the correct 3x3 result."""
        matrix = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        implementation(matrix) == ((1, 4, 7), (2, 5, 8), (3, 6, 9))

    def test_2_by_3_matrix(self, implementation):
        """Transposing a 2x3 matrix produces the correct 3x2 result."""
        matrix = ((1, 2, 3), (4, 5, 6))
        implementation(matrix) == ((1, 4), (2, 5), (3, 6))

    def test_3_by_2_matrix(self, implementation):
        """Transposing a 3x2 matrix produces the correct 2x3 result."""
        matrix = ((1, 2), (3, 4), (5, 6))
        implementation(matrix) == ((1, 3, 5), (2, 4, 6))


class TestIdentityMatrixAltHelpers:
    """Tests for the _kronecker_delta and _identity_matrix_row functions."""

    __slots__ = ()

    @pytest.mark.parametrize('i, j', [
        [0, 1], [0, 2], [0, 3],
        [1, 0], [1, 2], [1, 3],
        [2, 0], [2, 1], [2, 3],
        [3, 0], [3, 1], [3, 2],
    ])
    def test_kronecker_delta_is_0_with_not_equal_args(self, i, j):
        assert gencomp2._kronecker_delta(i, j) == 0

    @pytest.mark.parametrize('arg', [0, 1, 2, 3])
    def test_kronecker_delta_is_1_with_equal_args(self, arg):
        assert gencomp2._kronecker_delta(arg, arg) == 1

    @pytest.mark.parametrize('n, i, expected', [
        [1, 0, [1]],
        [2, 0, [1, 0]],
        [2, 1, [0, 1]],
        [3, 0, [1, 0, 0]],
        [3, 1, [0, 1, 0]],
        [3, 2, [0, 0, 1]],
        [4, 0, [1, 0, 0, 0]],
        [4, 1, [0, 1, 0, 0]],
        [4, 2, [0, 0, 1, 0]],
        [4, 3, [0, 0, 0, 1]],
        [5, 0, [1, 0, 0, 0, 0]],
        [5, 1, [0, 1, 0, 0, 0]],
        [5, 2, [0, 0, 1, 0, 0]],
        [5, 3, [0, 0, 0, 1, 0]],
        [5, 4, [0, 0, 0, 0, 1]],
    ])
    def test_identity_matrix_row(self, n, i, expected):
        assert gencomp2._identity_matrix_row(n, i) == expected


@pytest.mark.parametrize('implementation', [
    gencomp2.identity_matrix,
    gencomp2.identity_matrix_alt,
])
class TestIdentityMatrix:
    """Tests for the identity_matrix and identity_matrix_alt functions."""

    __slots__ = ()

    def test_0_by_0_is_empty_list(self, implementation):
        """The 0x0 identity matrix has no entries (no rows or columns)."""
        assert implementation(0) == []

    def test_1_by_1_consists_of_a_single_1_entry(self, implementation):
        """The 1x1 identity matrix has just one entry, a 1."""
        assert implementation(1) == [[1]]

    def test_1_by_1_entry_has_exact_type_int(self, implementation):
        """The 1x1 identity matrix's 1 entry is exactly int (not e.g. bool)."""
        id1 = implementation(1)
        entry = id1[0][0]
        assert type(entry) is int

    @pytest.mark.parametrize('n, expected', [
        [2, [[1, 0], [0, 1]]],
        [3, [[1, 0, 0], [0, 1, 0], [0, 0, 1]]],
        [4, [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]],
        [5,
         [[1, 0, 0, 0, 0],
          [0, 1, 0, 0, 0],
          [0, 0, 1, 0, 0],
          [0, 0, 0, 1, 0],
          [0, 0, 0, 0, 1]]],
        [6,
         [[1, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0],
          [0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 1]]],
        [7,
         [[1, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 1]]],
        [8,
         [[1, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 1]]],
        [9,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [10,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [11,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [12,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [13,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [14,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [15,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
        [16,
         [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]],
    ])
    def test_diagonal_are_1s_others_are_0s(self, implementation, n, expected):
        """Entries are the Kronecker delta function of the indices."""
        assert implementation(n) == expected

    @pytest.mark.parametrize('n', list(range(17)))
    def test_entries_have_exact_type_int(self, implementation, n):
        """Identity matrices' entries are all exactly int (not e.g. bool)."""
        result = implementation(n)
        assert all(type(entry) is int for row in result for entry in row)


@pytest.fixture(name='all_are_iterators')
def fixture_all_are_iterators():
    """Make a function that checks for an iterable of iterators."""
    return lambda rows: all(isinstance(row, Iterator) for row in rows)


class TestSubmap:
    """Tests for the submap function."""

    __slots__ = ()

    @pytest.mark.parametrize('rows', [
        [],
        (),
        set(),
        range(0),
        iter([]),
        iter(()),
        iter(set()),
        iter(range(0)),
    ])
    def test_empty_iterable_submaps_empty(self, rows):
        """Sub-mapping an empty iterable gives an empty iterator."""
        result = gencomp2.submap(len, rows)
        with pytest.raises(StopIteration):
            next(result)

    def test_iterable_of_heterogeneous_iterables(self, all_are_iterators):
        """Sub-mapping an iterable of different iterables maps each of them."""
        rows = reversed([iter(range(10)), (x - 1 for x in (1, 4, 7)), [2, 3]])
        result = gencomp2.submap(lambda x: x**2, rows)
        assert isinstance(result, Iterator)

        out_rows = list(result)
        assert all_are_iterators(out_rows)

        assert [list(out_row) for out_row in out_rows] == [
            [4, 9],
            [0, 9, 36],
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81],
        ]

    def test_iterable_of_strings(self, all_are_iterators):
        """Sub-mapping an iterable of strings maps each string's characters."""
        rows = ['Ifvsjtujdbmmz', 'Qsphsbnnfe', 'BMhpsjuinjd', 'Dpnqvufs']
        result = gencomp2.submap(lambda c: chr(ord(c) - 1), rows)
        assert isinstance(result, Iterator)

        out_rows = list(result)
        assert all_are_iterators(out_rows)

        assert [''.join(out_row) for out_row in out_rows] == [
            'Heuristically', 'Programmed', 'ALgorithmic', 'Computer'
        ]

    def test_iterable_of_iterable_of_sequence(self):
        """Sub-mapping a nested nested iterable maps the nested iterable."""
        rows = (([] for _ in range(1)) for _ in range(1))
        result = gencomp2.submap(len, rows)
        out_row = next(result)
        out_row_elem = next(out_row)

        assert out_row_elem == 0

        with pytest.raises(StopIteration):
            next(out_row)

        with pytest.raises(StopIteration):
            next(result)

    def test_duplicate_iterators_are_consumed(self, all_are_iterators):
        """Sub-mapping an iterable of iterators performs no materialization."""
        rows = [iter(range(1, 4))] * 2
        result = gencomp2.submap(lambda x: x, rows)
        assert isinstance(result, Iterator)

        out_rows = list(result)
        assert all_are_iterators(out_rows)

        assert [list(out_row) for out_row in out_rows] == [[1, 2, 3], []]


if __name__ == '__main__':
    sys.exit(pytest.main())
