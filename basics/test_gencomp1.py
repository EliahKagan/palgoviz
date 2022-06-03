#!/usr/bin/env python

"""Tests for gencomp1.py."""

from fractions import Fraction
import itertools
import sys

import pytest

import gencomp1
from testing import CommonIteratorTests


@pytest.mark.parametrize('implementation', [
    enumerate,  # Included to help test that the tests are correct.
    gencomp1.my_enumerate,
    gencomp1.my_enumerate_alt,
])
class TestMyEnumerate(CommonIteratorTests):
    """Tests for the my_enumerate and my_enumerate_alt functions."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(['ham', 'spam', 'eggs'])

    def test_enumerate_without_start_uses_zero_small(self, implementation):
        """All items are correct, paired with default 0-based indices."""
        iterable = ['ham', 'spam', 'eggs']
        result = implementation(iterable)
        assert list(result) == [(0, 'ham'), (1, 'spam'), (2, 'eggs')]

    def test_enumerate_without_start_uses_zero_big(self, implementation):
        """Items are produced lazily, paired with default 0-based indices."""
        iterable = range(3, 1_000_000_000_000_000_000_000_000_000_000_000, 2)
        result = implementation(iterable)
        prefix = list(itertools.islice(result, 6))
        assert prefix == [(0, 3), (1, 5), (2, 7), (3, 9), (4, 11), (5, 13)]

    def test_enumerate_with_start_uses_start_small(self, implementation):
        """All items are correct, paired with start and later indices."""
        iterable = ['ham', 'spam', 'eggs']
        result = implementation(iterable, 10)
        assert list(result) == [(10, 'ham'), (11, 'spam'), (12, 'eggs')]

    def test_enumerate_with_start_uses_start_big(self, implementation):
        """Items are produced lazily, paired with start and later indices."""
        iterable = range(3, 1_000_000_000_000_000_000_000_000_000_000_000, 2)
        result = implementation(iterable, 3)
        prefix = list(itertools.islice(result, 6))
        assert prefix == [(3, 3), (4, 5), (5, 7), (6, 9), (7, 11), (8, 13)]


@pytest.mark.parametrize('implementation', [
    gencomp1.print_enumerated,
    gencomp1.print_enumerated_alt,
])
class TestPrintEnumerated:
    """Tests for the print_enumerated and print_enumerated_alt functions."""

    __slots__ = ()

    @pytest.mark.parametrize('_label, kwargs', [
        ('implicit start', dict()),
        ('explicit start', dict(start=7)),
    ])
    def test_returns_none(self, implementation, _label, kwargs):
        """The function just prints. It is a conceptually void function."""
        assert implementation(**kwargs) is None

    def test_without_start_0_to_4_with_5_to_9(self, implementation, capsys):
        """Passing no argument prints messages for (0, 5) up to (4, 9)."""
        expected = (
            'index = 0, value = 5\n'
            'index = 1, value = 6\n'
            'index = 2, value = 7\n'
            'index = 3, value = 8\n'
            'index = 4, value = 9\n'
        )
        implementation()
        assert capsys.readouterr().out == expected

    def test_7_start_7_to_11_with_5_to_9(self, implementation, capsys):
        """Passing start=7 prints messages for (7, 5) up to (11, 9)."""
        expected = (
            'index = 7, value = 5\n'
            'index = 8, value = 6\n'
            'index = 9, value = 7\n'
            'index = 10, value = 8\n'
            'index = 11, value = 9\n'
        )
        implementation(start=7)
        assert capsys.readouterr().out == expected

    def test_start_argument_is_keyword_only(self, implementation):
        """Attempting to pass a positional argument raises TypeError."""
        with pytest.raises(TypeError):
            implementation(7)


@pytest.mark.parametrize('implementation', [
    any,  # Included to help test that the tests are correct.
    gencomp1.my_any,
])
class TestMyAny:
    """Tests for the my_any function."""

    __slots__ = ()

    def test_false_on_empty_iterable(self, implementation):
        """With no values, not even one is truthy, so any returns false."""
        assert implementation([]) is False

    @pytest.mark.parametrize('numbers', [
        range(1, 51),
        range(50),
        [17, 4, 9, 0, 3, 5, 0],
        [0, 0.0, 0, 0.0001, 0.0j, Fraction(0, 1)],
        [0, 0.0, 0, 0.0, 0.0j, Fraction(1, 1_000_000_000_000)],
    ])
    def test_true_on_numbers_including_nonzero(self, implementation, numbers):
        """So long as at least one number is not zero, any returns True."""
        assert implementation(numbers) is True

    def test_false_on_numbers_all_zero(self, implementation):
        assert implementation([0, 0.0, 0, Fraction(0, 1), 0, 0.0j]) is False

    def test_true_on_generator_with_some_truthy(self, implementation):
        """Iterators are accepted. If any item is truthy, it is reached."""
        assert implementation(x % 17 == 0 for x in range(100)) is True

    def test_false_on_generator_with_no_truthy(self, implementation):
        """Iterators are accepted. If no item is truthy, that is found out."""
        assert implementation(x > 100 for x in range(100)) is False

    def test_iterates_only_until_truthy(self, implementation):
        """Iterators are consumed, but only until a truthy item is found."""
        back = iter(range(100))
        front = (x % 17 == 0 for x in back)
        implementation(front)
        assert next(back) == 1

    def test_iterates_completely_if_nothing_is_truthy(self, implementation):
        """Iterators are consumed: consumed completely if no item is truthy."""
        back = iter(range(100))
        front = (x > 100 for x in back)
        implementation(front)
        with pytest.raises(StopIteration):
            next(back)


@pytest.mark.parametrize('implementation', [
    all,  # Included to help test that the tests are correct.
    gencomp1.my_all,
])
class TestMyAll:
    """Tests for the my_all function."""

    __slots__ = ()

    def test_true_on_empty_iterable(self, implementation):
        """With no values, not even one is falsy, so all returns true."""
        assert implementation([]) is True

    def test_false_on_numbers_including_zero(self, implementation):
        """So long as at least one number is zero, all returns False."""
        assert implementation([17, 4, 9, 0, 3, 5, 0]) is False

    @pytest.mark.parametrize('nonzero_numbers', [
        [1],
        [1, 1, 1, 6, 7, Fraction(1, 2)],
        [17, 4, 9, 0.0001, 3, 5, Fraction(1, 1_000_000_000_000), 0.0001j],
    ])
    def test_true_on_numbers_no_zeros(self, implementation, nonzero_numbers):
        assert implementation(nonzero_numbers)

    def test_false_on_nonempty_generator_with_all_falsy(self, implementation):
        """On nonempty input, False any() ensure False all()."""
        assert implementation(x > 100 for x in range(100)) is False

    def test_false_on_generator_with_some_falsy(self, implementation):
        """Iterators are accepted. If any item is falsy, it is reached."""
        assert implementation(x % 17 == 0 for x in range(100)) is False

    def test_true_on_generator_with_no_falsy(self, implementation):
        """Iterators are accepted. If no item is falsy, that is found out."""
        assert implementation(x % 17 == 0 for x in range(0, 100, 17)) is True

    def test_iterates_only_until_falsy(self, implementation):
        """Iterators are consumed, but only until a falsy item is found."""
        back = iter(range(100))
        front = (x % 17 == 0 for x in back)
        implementation(front)
        assert next(back) == 2

    def test_iterates_completely_if_nothing_is_falsy(self, implementation):
        """Iterators are consumed: consumed completely if no item is falsy."""
        back = iter(range(0, 100, 17))
        front = (x % 17 == 0 for x in back)
        implementation(front)
        with pytest.raises(StopIteration):
            next(back)


@pytest.mark.parametrize('implementation', [
    zip,  # Included to help test that the tests are correct.
    gencomp1.zip_two,
    gencomp1.my_zip,
])
class TestZipTwo(CommonIteratorTests):
    """Shared tests for the zip_two and my_zip functions."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation([10, 20, 30], ['foo', 'bar', 'baz'])

    def test_empty_iterables_zip_empty(self, implementation):
        """Zipping empty iterables yields no elements."""
        it = implementation([], [])
        with pytest.raises(StopIteration):
            next(it)

    def test_nonempty_empty_zips_empty(self, implementation):
        """Zipping a nonempty iterable with an empty one yields no elements."""
        it = implementation([10], [])
        with pytest.raises(StopIteration):
            next(it)

    def test_empty_nonempty_zips_empty(self, implementation):
        """Zipping an empty iterable with a nonempty one yields no elements."""
        it = implementation([], [10])
        with pytest.raises(StopIteration):
            next(it)

    def test_shorter_longer_zips_shorter(self, implementation):
        """Zipping a shorter iterable with a longer one works correctly."""
        it = implementation([10], [20, 30])
        assert list(it) == [(10, 20)]

    def test_longer_shorter_zips_shorter(self, implementation):
        """Zipping a longer iterable with a shorter one works correctly."""
        it = implementation([10, 20], [30])
        assert list(it) == [(10, 30)]

    def test_equal_lengths_zip_all(self, implementation):
        """Zipping iterables with equally many of elements works correctly."""
        it = implementation([10, 20, 30], ['foo', 'bar', 'baz'])
        assert list(it) == [(10, 'foo'), (20, 'bar'), (30, 'baz')]

    def test_finite_infinite_zips_finite(self, implementation):
        """Zipping a finite iterable with an infinite one works correctly."""
        it = implementation([10, 20, 30], itertools.count(1))
        assert list(it) == [(10, 1), (20, 2), (30, 3)]

    def test_infinite_finite_zips_finite(self, implementation):
        """Zipping an infinite iterable with a finite one works correctly."""
        it = implementation(itertools.count(1), [10, 20, 30])
        assert list(it) == [(1, 10), (2, 20), (3, 30)]


@pytest.mark.parametrize('implementation', [
    zip,  # Included to help test that the tests are correct.
    gencomp1.my_zip,
])
class TestMyZip:
    """Tests of the my_zip function (not shared with zip_two)."""

    __slots__ = ()

    def test_zero_args_zip_empty(self, implementation):
        """Passing zero iterables to be zipped yields no elements."""
        it = implementation()
        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize('single_arg', [[], ()])
    def test_single_empty_arg_zips_empty(self, implementation, single_arg):
        """Zipping a single empty iterable yields no elements."""
        it = implementation(single_arg)
        with pytest.raises(StopIteration):
            next(it)


class TestPrintZipped:
    """Tests for the print_zipped function."""

    __slots__ = ()

    def test_returns_none(self):
        """The function just prints. It is a conceptually void function."""
        assert gencomp1.print_zipped() is None

    def test_zipped_enumerated_data_are_printed(self, capsys):
        """Output strings represent 2-way zip of enumerated iterables."""
        expected = (
            "word_index=1, word='bat', number_index=100, number=1.5\n"
            "word_index=2, word='dog', number_index=101, number=2.5\n"
            "word_index=3, word='cat', number_index=102, number=3.5\n"
            "word_index=4, word='horse', number_index=103, number=4.5\n"
        )
        gencomp1.print_zipped()
        assert capsys.readouterr().out == expected


@pytest.mark.parametrize('implementation', [
    gencomp1.take_good,
    gencomp1.take,
])
class TestTake(CommonIteratorTests):
    """Tests for the take_good and take functions."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(range(3), 2)

    def test_taking_none_from_empty_is_empty(self, implementation):
        """Taking no items when there are no items yields no items."""
        it = implementation(range(0), 0)
        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_taking_some_from_empty_is_empty(self, implementation, n):
        """Taking some items when there are no items yields no items."""
        it = implementation(range(0), n)
        with pytest.raises(StopIteration):
            next(it)

    def test_taking_none_from_nonempty_is_empty(self, implementation):
        """Taking no items when there are some items yields no items."""
        it = implementation(range(3), 0)
        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize('n, expected', [
        (1, [0]),
        (2, [0, 1]),
        (3, [0, 1, 2]),
    ])
    def test_taking_some_from_nonempty_gives_prefix(self, implementation,
                                                    n, expected):
        """Taking some items when there are some items yields some items."""
        it = implementation(range(3), n)
        assert list(it) == expected

    @pytest.mark.parametrize('n', [4, 10, 100, 1_000_000])
    def test_taking_extra_from_nonempty_gives_all(self, implementation, n):
        """Taking too many items yields the existing items (without error)."""
        it = implementation(range(3), n)
        assert list(it) == [0, 1, 2]

    @pytest.mark.parametrize('n, expected', [
        (0, []),
        (1, [4]),
        (2, [4, 9]),
        (3, [4, 9, 16]),
        (4, [4, 9, 16, 25]),
        (5, [4, 9, 16, 25, 36]),
    ])
    def test_taking_from_infinite_gives_prefix(self, implementation,
                                               n, expected):
        """Taking some items from infinitely many items yields some items."""
        iterable = (x**2 for x in itertools.count(2))
        it = implementation(iterable, n)
        assert list(it) == expected

    def test_float_n_fails_fast(self, implementation):
        """Passing a float as the number of items raises TypeError."""
        with pytest.raises(TypeError, match=r"\An must be an int\Z"):
            implementation(range(5), 1.0)

    def test_negative_n_fails_fast(self, implementation):
        """Passing a negative int as the number of items raises ValueError."""
        expected_message = r"\Acan't yield negatively many items\Z"
        with pytest.raises(ValueError, match=expected_message):
            implementation(range(5), -1)

    def test_negative_float_fails_fast_as_float(self, implementation):
        """Passing a negative float as hte number of items raises TypeError."""
        with pytest.raises(TypeError, match=r"\An must be an int\Z"):
            implementation(range(5), -1.0)

    @pytest.mark.parametrize('n, expected', [
        (False, []),
        (True, ['p']),
    ])
    def test_bool_n_is_supported(self, implementation, n, expected):
        """n is allowed to be a bool, since bool is a subclass of int."""
        it = implementation('pqr', n)
        assert list(it) == expected

    def test_input_is_not_overconsumed(self, implementation):
        """No more than n elements of the input are consumed."""
        it = (x**2 for x in range(1, 6))

        # Take 2 items from the iterator. Stop with an error if that failed.
        if list(implementation(it, 2)) != [1, 4]:
            raise Exception("Can't test overconsumption (first call failed)")

        assert list(it) == [9, 16, 25], "Make sure we didn't consume too much."


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
