#!/usr/bin/env python

# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""Tests for gencomp1.py."""

# FIXME: Add missing tests (search for "FIXME"). Then remove this FIXME too.

from fractions import Fraction
import itertools
import operator
import random
import string
import sys

import pytest

from palgoviz import gencomp1
from tests import _helpers


class _IterCountingMixin:
    """
    A mixin for making classes that count calls to their __iter__ method.

    List this immediately before an iterable base class, when inheriting.
    """

    iter_calls = 0

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    def __iter__(self):
        self.iter_calls += 1
        return super().__iter__()


class _IterCountingList(_IterCountingMixin, list):
    """
    A list that counts how many times __iter__ is called on it.

    This is used in the TestTailOpt and TestLengthOfOpt test classes (below).
    """


class _IterCountingSet(_IterCountingMixin, set):
    """
    A set that counts how many times __iter__ is called on it.

    This is used in the TestLengthOfOpt test class (below).
    """


class _IterCountingDict(_IterCountingMixin, dict):
    """
    A dict that counts how many times __iter__ is called on it.

    This is used in the TestLengthOfOpt test class (below).
    """


@pytest.mark.parametrize('implementation', [
    enumerate,  # Included to help test that the tests are correct.
    gencomp1.my_enumerate,
    gencomp1.my_enumerate_alt,
    gencomp1.Enumerate,
])
class TestEnumerate(_helpers.CommonIteratorTests):
    """Tests for my_enumerate and related functions and classes."""

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
    gencomp1.my_any_alt,
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
    gencomp1.my_all_alt,
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
    gencomp1.ZipTwo,
    gencomp1.my_zip,
    gencomp1.Zip,
])
class TestZipTwo(_helpers.CommonIteratorTests):
    """Shared tests for the zip_two/ZipTwo and my_zip/Zip functions/classes."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation([10, 20, 30], ['foo', 'bar', 'baz'])

    def test_empty_iterables_zip_empty(self, implementation):
        """Zipping empty iterables yields no elements."""
        result = implementation([], [])
        with pytest.raises(StopIteration):
            next(result)

    def test_nonempty_empty_zips_empty(self, implementation):
        """Zipping a nonempty iterable with an empty one yields no elements."""
        result = implementation([10], [])
        with pytest.raises(StopIteration):
            next(result)

    def test_empty_nonempty_zips_empty(self, implementation):
        """Zipping an empty iterable with a nonempty one yields no elements."""
        result = implementation([], [10])
        with pytest.raises(StopIteration):
            next(result)

    def test_shorter_longer_zips_shorter(self, implementation):
        """Zipping a shorter iterable with a longer one works correctly."""
        result = implementation([10], [20, 30])
        assert list(result) == [(10, 20)]

    def test_longer_shorter_zips_shorter(self, implementation):
        """Zipping a longer iterable with a shorter one works correctly."""
        result = implementation([10, 20], [30])
        assert list(result) == [(10, 30)]

    def test_equal_lengths_zip_all(self, implementation):
        """Zipping iterables with equally many of elements works correctly."""
        result = implementation([10, 20, 30], ['foo', 'bar', 'baz'])
        assert list(result) == [(10, 'foo'), (20, 'bar'), (30, 'baz')]

    def test_finite_infinite_zips_finite(self, implementation):
        """Zipping a finite iterable with an infinite one works correctly."""
        result = implementation([10, 20, 30], itertools.count(1))
        assert list(result) == [(10, 1), (20, 2), (30, 3)]

    def test_infinite_finite_zips_finite(self, implementation):
        """Zipping an infinite iterable with a finite one works correctly."""
        result = implementation(itertools.count(1), [10, 20, 30])
        assert list(result) == [(1, 10), (2, 20), (3, 30)]


@pytest.mark.parametrize('implementation', [
    zip,  # Included to help test that the tests are correct.
    gencomp1.my_zip,
    gencomp1.Zip,
])
class TestZip(_helpers.CommonIteratorTests):
    """Tests of the my_zip function and Zip class (not shared with zip_two)."""

    __slots__ = ()

    def test_zero_args_zip_empty(self, implementation):
        """Passing zero iterables to be zipped yields no elements."""
        result = implementation()
        with pytest.raises(StopIteration):
            next(result)

    @pytest.mark.parametrize('single_arg', [[], ()])
    def test_single_empty_arg_zips_empty(self, implementation, single_arg):
        """Zipping a single empty iterable yields no elements."""
        result = implementation(single_arg)
        with pytest.raises(StopIteration):
            next(result)


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
    gencomp1.Take,
])
class TestTake(_helpers.CommonIteratorTests):
    """Tests for take and related functions and classes."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(range(3), 2)

    def test_taking_none_from_empty_is_empty(self, implementation):
        """Taking no items when there are no items yields no items."""
        result = implementation(range(0), 0)
        with pytest.raises(StopIteration):
            next(result)

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_taking_some_from_empty_is_empty(self, implementation, n):
        """Taking some items when there are no items yields no items."""
        result = implementation(range(0), n)
        with pytest.raises(StopIteration):
            next(result)

    def test_taking_none_from_nonempty_is_empty(self, implementation):
        """Taking no items when there are some items yields no items."""
        result = implementation(range(3), 0)
        with pytest.raises(StopIteration):
            next(result)

    @pytest.mark.parametrize('n, expected', [
        (1, [0]),
        (2, [0, 1]),
        (3, [0, 1, 2]),
    ])
    def test_taking_some_from_nonempty_gives_prefix(self, implementation,
                                                    n, expected):
        """Taking some items when there are some items yields some items."""
        result = implementation(range(3), n)
        assert list(result) == expected

    @pytest.mark.parametrize('n', [4, 10, 100, 1_000_000])
    def test_taking_extra_from_nonempty_gives_all(self, implementation, n):
        """Taking too many items yields the existing items (without error)."""
        result = implementation(range(3), n)
        assert list(result) == [0, 1, 2]

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
        result = implementation(iterable, n)
        assert list(result) == expected

    def test_float_n_fails_fast(self, implementation):
        """Passing a float as the number of items raises TypeError."""
        with pytest.raises(TypeError, match=r"\An must be an int\Z"):
            implementation(range(5), 1.0)

    def test_negative_n_fails_fast(self, implementation):
        """Passing a negative int as the number of items raises ValueError."""
        expected_message = r"\Acan't yield negatively many items\Z"
        with pytest.raises(ValueError, match=expected_message):
            implementation(range(5), -1)

    def test_negative_float_n_fails_fast_as_float(self, implementation):
        """Passing a negative float as the number of items raises TypeError."""
        with pytest.raises(TypeError, match=r"\An must be an int\Z"):
            implementation(range(5), -1.0)

    @pytest.mark.parametrize('n, expected', [
        (False, []),
        (True, ['p']),
    ])
    def test_bool_n_is_supported(self, implementation, n, expected):
        """n is allowed to be a bool, since bool is a subclass of int."""
        result = implementation('pqr', n)
        assert list(result) == expected

    def test_input_is_not_overconsumed(self, implementation):
        """No more than n elements of the input are consumed."""
        it = (x**2 for x in range(1, 6))

        # Take 2 items from the iterator. Stop with an error if that failed.
        if list(implementation(it, 2)) != [1, 4]:
            raise Exception("Can't test overconsumption (first call failed)")

        assert list(it) == [9, 16, 25], "Make sure we didn't consume too much."


@pytest.mark.parametrize('implementation', [
    gencomp1.drop_good,
    gencomp1.drop,
    gencomp1.Drop,
])
class TestDrop(_helpers.CommonIteratorTests):
    """Tests for drop and related functions and classes."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(range(5), 2)

    def test_dropping_none_from_empty_is_empty(self, implementation):
        """Dropping no items when there are no items yields no items."""
        result = implementation(range(0), 0)
        with pytest.raises(StopIteration):
            next(result)

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_dropping_some_from_empty_is_empty(self, implementation, n):
        """
        Dropping some items when there are none yields none (without error).
        """
        result = implementation(range(0), n)
        with pytest.raises(StopIteration):
            next(result)

    def test_dropping_none_from_nonempty_gives_all(self, implementation):
        """Dropping no items when there are some items yields all the items."""
        result = implementation(range(5), 0)
        assert list(result) == [0, 1, 2, 3, 4]

    @pytest.mark.parametrize('n, expected', [
        (1, [1, 2, 3, 4]),
        (2, [2, 3, 4]),
        (3, [3, 4]),
        (4, [4]),
    ])
    def test_dropping_some_from_nonempty_gives_suffix(self, implementation,
                                                      n, expected):
        """Dropping some items when there are some items yields the rest."""
        result = implementation(range(5), n)
        assert list(result) == expected

    def test_dropping_all_from_nonempty_is_empty(self, implementation):
        """Dropping all items when there are some items yields no items."""
        result = implementation(range(5), 5)
        with pytest.raises(StopIteration):
            next(result)

    @pytest.mark.parametrize('n', [6, 7, 15, 100, 1_000_000])
    def test_dropping_extra_from_nonempty_is_empty(self, implementation, n):
        """Dropping more than all items yields no items (without error)."""
        result = implementation(range(5), n)
        with pytest.raises(StopIteration):
            next(result)

    def test_dropping_some_from_infinite_gives_rest(self, implementation):
        """
        Dropping some items when there are infinitely many yields the rest.
        """
        result = implementation(itertools.count(1), 1000)
        prefix_of_suffix = itertools.islice(result, 6)
        assert list(prefix_of_suffix) == [1001, 1002, 1003, 1004, 1005, 1006]

    def test_float_n_fails_fast(self, implementation):
        """Passing a float as the number of items raises TypeError."""
        with pytest.raises(TypeError, match=r"\An must be an int\Z"):
            implementation(range(5), 1.0)

    def test_negative_n_fails_fast(self, implementation):
        """Passing a negative int as the number of items raises ValueError."""
        expected_message = r"\Acan't skip negatively many items\Z"
        with pytest.raises(ValueError, match=expected_message):
            implementation(range(5), -1)

    def test_negative_float_n_fails_fast_as_float(self, implementation):
        """Passing a negative float as the number of items raises TypeError."""
        with pytest.raises(TypeError, match=r"\An must be an int\Z"):
            implementation(range(5), -1.0)

    @pytest.mark.parametrize('n, expected', [
        (False, ['p', 'q', 'r']),
        (True, ['q', 'r']),
    ])
    def test_bool_n_is_supported(self, implementation, n, expected):
        """n is allowed to be a bool, since bool is a subclass of int."""
        result = implementation('pqr', n)
        assert list(result) == expected


class TestLast:
    """Tests for the last function."""

    __slots__ = ()

    def test_empty_iterable_has_no_last_item(self):
        """On a generator yielding no items, IndexError is raised."""
        expected_message = r"\Acan't get last item from empty iterable\Z"
        with pytest.raises(IndexError, match=expected_message):
            gencomp1.last(x for x in ())

    def test_last_of_singleton_iterator_is_the_item(self):
        """On a generator yielding exactly one item, that item is returned."""
        result = gencomp1.last(x for x in (10,))
        assert result == 10

    def test_last_of_sequence_is_item_at_end(self):
        """On a sequence of several items, the item at index -1 is returned."""
        result = gencomp1.last(['foo', 'bar', 'baz', 'quux', 'foobar'])
        assert result == 'foobar'

    def test_last_of_iterator_is_final_item(self):
        """On an iterator to a fairly big range, the final item is returned."""
        it = iter(range(100_000))
        assert gencomp1.last(it) == 99_999

    def test_last_of_nonempty_string_is_ending_character(self):
        """A nonempty string's length-1 substring at the end is returned."""
        text = 'I code in all the scary animals in my house including Python'
        assert gencomp1.last(text) == 'n'


@pytest.mark.parametrize('implementation', [
    gencomp1.tail,
    gencomp1.tail_opt,
])
class TestTail:
    """Shared tests for the tail and tail_opt functions."""

    __slots__ = ()

    def test_empty_suffix_of_empty_sequence_is_empty(self, implementation):
        """No items taken from the end of no items are no items."""
        assert implementation([], 0) == ()

    def test_empty_suffix_of_empty_iterator_is_empty(self, implementation):
        """No items taken from the end of no items are no items."""
        assert implementation(iter([]), 0) == ()

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_all_suffixes_of_empty_sequence_are_empty(self, implementation, n):
        """Trying to take some items from the end of no items gets no items."""
        assert implementation([], n) == ()

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_all_suffixes_of_empty_iterator_are_empty(self, implementation, n):
        """Trying to take some items from the end of no items gets no items."""
        assert implementation(iter([]), n) == ()

    def test_empty_suffix_of_nonempty_sequence_is_empty(self, implementation):
        """No items taken from the end of some items are no items."""
        sequence = [x**2 for x in range(100)]
        assert implementation(sequence, 0) == ()

    def test_empty_suffix_of_nonempty_iterator_is_empty(self, implementation):
        """No items taken from the end of some items are no items."""
        iterator = (x**2 for x in range(100))
        assert implementation(iterator, 0) == ()

    @pytest.mark.parametrize('n, expected', [
        (1, (9801,)),
        (2, (9604, 9801)),
        (3, (9409, 9604, 9801)),
        (4, (9216, 9409, 9604, 9801)),
        (5, (9025, 9216, 9409, 9604, 9801)),
    ])
    def test_short_suffix_of_long_sequence_is_full_short(self, implementation,
                                                         n, expected):
        """Taking a few items from end of many items gets those few items."""
        sequence = [x**2 for x in range(100)]
        assert implementation(sequence, n) == expected

    @pytest.mark.parametrize('n, expected', [
        (1, (9801,)),
        (2, (9604, 9801)),
        (3, (9409, 9604, 9801)),
        (4, (9216, 9409, 9604, 9801)),
        (5, (9025, 9216, 9409, 9604, 9801)),
    ])
    def test_short_suffix_of_long_iterator_is_full_short(self, implementation,
                                                         n, expected):
        """Taking a few items from end of many items gets those few items."""
        iterator = (x**2 for x in range(100))
        assert implementation(iterator, n) == expected


@pytest.mark.parametrize('_label, iterator_factory', [
    ('generator, length 100', lambda: (x**2 for x in range(100))),
    ('range iterator, length 1000', lambda: iter(range(1000))),
])
def test_empty_tail_consumes_all_input(_label, iterator_factory):
    """
    The tail function always iterates through its input completely.

    Even though, with n=0, this is not needed to give the correct result, it is
    still done for consistency. This test checks that empty (n=0) case.

    This does not apply to tail_opt, which doesn't otherwise enjoy consistency
    in whether or not or how much it consumes its input, anyway. The tail_opt
    function or may or may not iterate through input when n=0.
    """
    iterator = iterator_factory()
    result = gencomp1.tail(iterator, 0)

    if result != ():
        raise Exception("Can't test if input was consumed, as tail failed")

    with pytest.raises(StopIteration):
        next(iterator)


class TestTailOpt:
    """Tests specific to the tail_opt function."""

    __slots__ = ()

    @pytest.mark.parametrize('n', [6, 5, 4])
    def test_total_suffixes_of_sequence_work_without_iter(self, subtests, n):
        """Improper suffixes (whole sequence) are found without __iter__."""
        sequence = _IterCountingList([10, 20, 30, 40])
        result = gencomp1.tail_opt(sequence, n)
        with subtests.test('Result should be correct'):
            assert result == (10, 20, 30, 40)
        with subtests.test('__iter__ should not be called'):
            assert sequence.iter_calls == 0

    @pytest.mark.parametrize('n, expected', [
        (3, (20, 30, 40)),
        (2, (30, 40)),
        (1, (40,)),
        (0, ()),
    ])
    def test_partial_suffixes_of_sequence_work_without_iter(self, subtests,
                                                            n, expected):
        """Trailing pieces of sequences are found without __iter__."""
        sequence = _IterCountingList([10, 20, 30, 40])
        result = gencomp1.tail_opt(sequence, n)
        with subtests.test('Result should be correct'):
            assert result == expected
        with subtests.test('__iter__ should not be called'):
            assert sequence.iter_calls == 0

    def test_iter_called_once_on_nonsequence(self, subtests):
        """Finding a suffix of a non-sequence iterable calls __iter__ once."""
        sequence = _IterCountingList([10, 20, 30, 40])
        indirect_iterator = itertools.chain(sequence)

        if sequence.iter_calls != 0:
            raise Exception("itertools.chain shouldn't call __iter__ eagerly")

        result = gencomp1.tail_opt(indirect_iterator, 3)

        with subtests.test('Result should be correct'):
            assert result == (20, 30, 40)

        with subtests.test('__iter__ should be called once'):
            assert sequence.iter_calls == 1

    def test_small_suffix_of_huge_sequence_is_computed_quickly(self):
        """
        A suffix is found, where it would never manage to finish via __iter__.

        This effectively tests if slicing is used.
        """
        result = gencomp1.tail_opt(range(1_000_000_000_000), 5)

        assert result == (999999999995, 999999999996, 999999999997,
                          999999999998, 999999999999)

    def test_falls_back_to_iter_with_len_but_not_indexing(self):
        """If the input supports len but indexing/slicing, __iter__ is used."""
        iterable = dict.fromkeys(range(1000))
        result = gencomp1.tail_opt(iterable, 3)
        assert result == (997, 998, 999)

    def test_falls_back_to_iter_with_indexing_but_not_slicing(self):
        """If the input supports indexing but not slicing, __iter__ is used."""
        iterable = {'a', 'b', 'c', 'd', 'e'}
        result = gencomp1.tail_opt(iterable, 128)
        assert sorted(result) == ['a', 'b', 'c', 'd', 'e']


class TestPick:
    """Tests for the pick function."""

    __slots__ = ()

    @pytest.mark.parametrize('items', [
        (),
        (10,),
        (10, 20),
        (10, 20, 30),
    ])
    def test_index_after_end_is_error(self, subtests, items):
        """Passing a too-large int as index value raises IndexError."""
        expected_message = r'\Aindex out of range\Z'
        for index in range(len(items), len(items) + 3):
            with subtests.test(index=index):
                generator = (x for x in items)
                with pytest.raises(IndexError, match=expected_message):
                    gencomp1.pick(generator, index)

    @pytest.mark.parametrize('index', [-1, -2, -10, -100])
    def test_negative_index_is_error(self, index):
        """Passing a negative int as index value raises IndexError."""
        expected_message = r'\Anegative indices are not supported\Z'
        generator = (x for x in (10,))
        with pytest.raises(IndexError, match=expected_message):
            gencomp1.pick(generator, index)

    @pytest.mark.parametrize('items', [
        (10,),
        (10, 20),
        (10, 20, 30),
    ])
    def test_index_zero_is_first_item(self, items):
        """Passing an index of zero gets the first item."""
        generator = (x for x in items)
        assert gencomp1.pick(generator, 0) == 10

    @pytest.mark.parametrize('index, expected', [
        (1, 3),
        (2, 5),
        (15, 31),
        (100, 201),
        (1017, 2035),
        (4422, 8845),
    ])
    def test_indexing_into_sequence_gets_value(self, index, expected):
        """Accessing the k index of a sequence seq agrees with seq[k]."""
        sequence = range(1, 10_000, 2)
        assert gencomp1.pick(sequence, index) == expected

    @pytest.mark.parametrize('index, expected', [
        (1, 3),
        (2, 5),
        (15, 31),
        (100, 201),
        (1017, 2035),
        (4422, 8845),
    ])
    def test_indexing_into_iterator_gets_value(self, index, expected):
        """Accessing the k index of an iterator skips k items and gets next."""
        iterator = iter(range(1, 10_000, 2))
        assert gencomp1.pick(iterator, index) == expected


@pytest.mark.parametrize('implementation', [
    gencomp1.windowed,
    gencomp1.Windowed,
    gencomp1.windowed_alt,
])
class TestWindowed(_helpers.CommonIteratorTests):
    """Tests for windowed and related functions and classes."""

    __slots__ = ()

    def instantiate(self, implementation):
        input_it = map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk'])
        return implementation(input_it, 3)

    def test_empty_input_has_one_empty_window(self, implementation):
        """With no items, there is one window containing no items."""
        result = implementation((), 0)
        assert list(result) == [()]

    @pytest.mark.parametrize('n', [1, 2, 10, 100])
    def test_empty_input_has_no_nonempty_windows(self, implementation, n):
        """With no items, there are no windows containing any items."""
        result = implementation((), n)
        with pytest.raises(StopIteration):
            next(result)

    @pytest.mark.parametrize('n, expected', [
        (0, [(), (), (), (), (), ()]),
        (1, [('ab',), ('cd',), ('efg',), ('hi',), ('jk',)]),
        (2, [('ab', 'cd'), ('cd', 'efg'), ('efg', 'hi'), ('hi', 'jk')]),
        (3, [('ab', 'cd', 'efg'), ('cd', 'efg', 'hi'), ('efg', 'hi', 'jk')]),
        (4, [('ab', 'cd', 'efg', 'hi'), ('cd', 'efg', 'hi', 'jk')]),
        (5, [('ab', 'cd', 'efg', 'hi', 'jk')]),
        (6, []),
        (7, []),
        (100, []),
        (1_000_000, []),
    ])
    def test_small_nontrivial_sequence_has_all_windows(self, implementation,
                                                       n, expected):
        """All windows of any size are found in a small nontrivial sequence."""
        sequence = ['ab', 'cd', 'efg', 'hi', 'jk']
        result = implementation(sequence, n)
        assert list(result) == expected

    @pytest.mark.parametrize('n, expected', [
        (0, [(), (), (), (), (), ()]),
        (1, [('Ab',), ('Cd',), ('Efg',), ('Hi',), ('Jk',)]),
        (2, [('Ab', 'Cd'), ('Cd', 'Efg'), ('Efg', 'Hi'), ('Hi', 'Jk')]),
        (3, [('Ab', 'Cd', 'Efg'), ('Cd', 'Efg', 'Hi'), ('Efg', 'Hi', 'Jk')]),
        (4, [('Ab', 'Cd', 'Efg', 'Hi'), ('Cd', 'Efg', 'Hi', 'Jk')]),
        (5, [('Ab', 'Cd', 'Efg', 'Hi', 'Jk')]),
        (6, []),
        (7, []),
        (100, []),
        (1_000_000, []),
    ])
    def test_small_nontrivial_iterator_has_all_windows(self, implementation,
                                                       n, expected):
        """All windows of any size are found in a small nontrivial iterator."""
        iterator = map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk'])
        result = implementation(iterator, n)
        assert list(result) == expected

    def test_huge_sequence_windows_are_yielded_lazily(self, implementation):
        """On a very big input sequence, the first few windows can be got."""
        sequence = range(1_000_000_000_000)
        expected = [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]
        result = implementation(sequence, 3)
        prefix = itertools.islice(result, 5)
        assert list(prefix) == expected

    def test_huge_iterator_windows_are_yielded_lazily(self, implementation):
        """On a very big input iterator, the first few windows can be got."""
        iterator = iter(range(1_000_000_000_000))
        expected = [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]
        result = implementation(iterator, 3)
        prefix = itertools.islice(result, 5)
        assert list(prefix) == expected


# FIXME: gencomp1.my_pairwise and gencomp1.Pairwise still need pytest tests.


@pytest.mark.parametrize('implementation', [
    map,  # Included to help test that the tests are correct.
    gencomp1.map_one,
    gencomp1.map_one_alt,
    gencomp1.MapOne,
])
class TestMapOne(_helpers.CommonIteratorTests):
    """Tests for map_one and related functions and classes."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(str.capitalize, ['foo', 'bar', 'baz', 'quux'])

    def test_empty_sequence_maps_empty(self, implementation):
        """Mapping a sequence of no items gives no items."""
        result = implementation(lambda x: x**2, range(0))
        with pytest.raises(StopIteration):
            next(result)

    def test_empty_iterator_maps_empty(self, implementation):
        """Mapping a generator of no items gives no items."""
        result = implementation(lambda x: x + 1, (x**2 for x in range(0)))
        with pytest.raises(StopIteration):
            next(result)

    def test_sequence_maps_via_python_function_1(self, implementation):
        """Mapping a range via a Python function (lambda) works."""
        result = implementation(lambda x: x**2, range(1, 11))
        assert list(result) == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

    def test_iterator_maps_via_python_function_1(self, implementation):
        """Mapping a range iterator via a Python function (lambda) works."""
        result = implementation(lambda x: x**2, iter(range(1, 11)))
        assert list(result) == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

    def test_sequence_maps_via_python_function_2(self, implementation):
        """Mapping a list via a Python function (lambda) works."""
        result = implementation(lambda x: x + 1, [x**2 for x in range(1, 6)])
        assert list(result) == [2, 5, 10, 17, 26]

    def test_iterator_maps_via_python_function_2(self, implementation):
        """Mapping a generator via a Python function (lambda) works."""
        result = implementation(lambda x: x + 1, (x**2 for x in range(1, 6)))
        assert list(result) == [2, 5, 10, 17, 26]

    def test_sequence_maps_via_builtin_function(self, implementation):
        """Mapping a list via a top-level builtin function works."""
        result = implementation(len, ['foobar', (10, 20), range(1000)])
        assert list(result) == [6, 2, 1000]

    def test_iterator_maps_via_builtin_function(self, implementation):
        """Mapping a list iterator vai a top-level builtin function works."""
        result = implementation(len, iter(['foobar', (10, 20), range(1000)]))
        assert list(result) == [6, 2, 1000]

    def test_sequence_maps_via_builtin_method(self, implementation):
        """Mapping a list via a method on a builtin type works."""
        result = implementation(str.capitalize, ['foo', 'bar', 'baz', 'quux'])
        assert list(result) == ['Foo', 'Bar', 'Baz', 'Quux']

    def test_iterator_maps_via_builtin_method(self, implementation):
        """Mapping a list iterator via a method on a builtin type works."""
        iterator = iter(['foo', 'bar', 'baz', 'quux'])
        result = implementation(str.capitalize, iterator)
        assert list(result) == ['Foo', 'Bar', 'Baz', 'Quux']

    def test_infinite_iterator_maps_lazily(self, implementation):
        """We can get a prefix, mapping an infinite iterator."""
        expected = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2]
        result = implementation(int.bit_count, itertools.count())
        prefix = itertools.islice(result, 18)
        assert list(prefix) == expected

    def test_func_must_be_callable_not_none(self, implementation):
        """None isn't treated as an identity function (unlike filter)."""
        with pytest.raises(TypeError):
            list(implementation(None, [0]))


@pytest.mark.parametrize('implementation', [
    filter,  # Included to help test that the tests are correct.
    gencomp1.my_filter,
    gencomp1.my_filter_alt,
    gencomp1.Filter,
])
class TestFilter(_helpers.CommonIteratorTests):
    """Tests for my_filter and related functions and classes."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(operator.not_, [0, 1, 2, 0, 2, 0, 0, 1])

    def test_none_satisfying_is_empty_from_sequence(self, implementation):
        """When no items satisfy the predicate, the result is empty."""
        numbers = (0, 1, 2)
        result = implementation(lambda n: n < 0, numbers)
        with pytest.raises(StopIteration):
            next(result)

    def test_none_satisfying_is_empty_from_iterator(self, implementation):
        """When no items satisfy the predicate, the result is empty."""
        numbers = iter((0, 1, 2))
        result = implementation(lambda n: n < 0, numbers)
        with pytest.raises(StopIteration):
            next(result)

    def test_some_satisfying_gives_those_from_sequence(self, implementation):
        """When only some satisfy the predicate, those are the result."""
        words = ['ham', 'spam', 'foo', 'eggs']
        result = implementation(lambda x: len(x) == 3, words)
        assert list(result) == ['ham', 'foo']

    def test_some_satisfying_gives_those_from_iterator(self, implementation):
        """When only some satisfy the predicate, those are the result."""
        words = iter(['ham', 'spam', 'foo', 'eggs'])
        result = implementation(lambda x: len(x) == 3, words)
        assert list(result) == ['ham', 'foo']

    def test_none_predicate_filters_truthy_from_sequence(self, implementation):
        """A predicate of None checks the items themselves."""
        mixed = ('p', 'xy', [3], (1, 2, 3), 'c')
        suffixes = [seq[1:] for seq in mixed]
        result = implementation(None, suffixes)
        assert list(result) == ['y', (2, 3)]

    def test_none_predicate_filters_truthy_from_iterator(self, implementation):
        """A predicate of None checks the items themselves."""
        mixed = ('p', 'xy', [3], (1, 2, 3), 'c')
        suffixes = (seq[1:] for seq in mixed)
        result = implementation(None, suffixes)
        assert list(result) == ['y', (2, 3)]

    def test_none_predicate_filters_truthy_even_if_none_from_sequence(
            self,
            implementation):
        """A predicate of None gets nothing through if all are falsy."""
        empties = [[], (), {}, set()]
        result = implementation(None, empties)
        with pytest.raises(StopIteration):
            next(result)

    def test_none_predicate_filters_truthy_even_if_none_from_iterator(
            self,
            implementation):
        """A predicate of None gets nothing through if all are falsy."""
        empties = iter([[], (), {}, set()])
        result = implementation(None, empties)
        with pytest.raises(StopIteration):
            next(result)

    def test_none_predicate_filters_truthy_even_if_all_from_sequence(
            self,
            implementation):
        """A predicate of None lets everything through if none are falsy."""
        words = ['hello', 'glorious', 'world']
        result = implementation(None, words)
        assert list(result) == ['hello', 'glorious', 'world']

    def test_none_predicate_filters_truthy_even_if_all_from_iterator(
            self,
            implementation):
        """A predicate of None lets everything through if none are falsy."""
        words = iter(['hello', 'glorious', 'world'])
        result = implementation(None, words)
        assert list(result) == ['hello', 'glorious', 'world']

    def test_infinite_iterator_filters_lazily(self, implementation):
        """We can get a prefix, filtering a some-truthy infinite iterator."""
        result = implementation(lambda k: k % 2, itertools.count())
        prefix = itertools.islice(result, 13)
        assert list(prefix) == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]


@pytest.mark.parametrize('implementation', [
    gencomp1.length_of,
    gencomp1.length_of_opt,
])
class TestLengthOf:
    """Tests for the length_of and length_of_opt functions."""

    __slots__ = ()

    def test_empty_sequence_has_length_zero(self, implementation):
        """The length of a zero-element tuple is zero."""
        assert implementation(()) == 0

    def test_empty_iterator_has_length_zero(self, implementation):
        """The length of a zero-element generator is zero."""
        assert implementation(x for x in ()) == 0

    def test_short_sequence_has_its_length(self, implementation):
        """
        The length of a list of two items is 2.

        The strangely complicated way this input is produced is for contrast to
        test_short_generator_has_its_length (below), where I think a generator
        expression with an "if" clause is helpfully illustrative.
        """
        strings = ['ham', 'spam', 'foo', 'eggs', '']
        sequence = [s for s in strings if len(s) == 3]
        assert implementation(sequence) == 2

    def test_short_iterator_has_its_length(self, implementation):
        """The length of a generator of two items is 2."""
        strings = ['ham', 'spam', 'foo', 'eggs', '']
        iterator = (s for s in strings if len(s) == 3)
        assert implementation(iterator) == 2

    def test_moderately_long_sequence_has_its_length(self, implementation):
        """The length of a 1000-element range is 1000."""
        assert implementation(range(1000)) == 1000

    def test_moderately_long_iterator_has_its_length(self, implementation):
        """The length of a 1000-element generator is 1000."""
        assert implementation(x + 27 for x in range(1000)) == 1000

    def test_pretty_big_set_has_its_length(self, implementation):
        """The length of a 100,000-element set is 100,000."""
        objects = {object() for _ in range(100_000)}
        assert implementation(objects) == 100_000

    def test_pretty_long_iterator_has_its_length(self, implementation):
        """The length of a 100,000-element generator is 100,000."""
        iterator = (object() for _ in range(100_000))
        assert implementation(iterator) == 100_000


class TestLengthOfOpt:
    """Tests specific to the length_of_opt function."""

    __slots__ = ()

    def test_empty_sequence_works_without_iter(self, subtests):
        """
        __iter__ is not called on an empty sequence.

        Even though it involves some undesirable repetition, I think it's
        beneficial to name this separately from the "nonempty" version, so it
        is easier to see which of the empty and nonempty cases are failing in a
        buggy implementation.
        """
        sequence = _IterCountingList()
        result = gencomp1.length_of_opt(sequence)
        with subtests.test('Result should be correct'):
            assert result == 0
        with subtests.test('__iter__ should not be called'):
            assert sequence.iter_calls == 0

    @pytest.mark.parametrize('items, length', [
        ([0], 1),
        ([10, 20], 2),
        (['foo', 'bar', 'baz'], 3),
        (range(1000), 1000),
    ])
    def test_nonempty_sequence_works_without_iter(self, subtests,
                                                  items, length):
        """__iter__ is not called on a nonempty sequence."""
        sequence = _IterCountingList(items)
        result = gencomp1.length_of_opt(sequence)
        with subtests.test('Result should be correct'):
            assert result == length
        with subtests.test('__iter__ should not be called'):
            assert sequence.iter_calls == 0

    @pytest.mark.parametrize('sequence_type', [
        _IterCountingSet,
        _IterCountingDict,
    ])
    def test_empty_sized_nonsequence_works_without_iter(self, subtests,
                                                        sequence_type):
        """
        __iter__ is not called on an empty non-sequence supporting len.

        See test_empty_sequence_works_without_iter on why this is separate.
        """
        sized = sequence_type()
        result = gencomp1.length_of_opt(sized)
        with subtests.test('Result should be correct'):
            assert result == 0
        with subtests.test('__iter__ should not be called'):
            assert sized.iter_calls == 0

    @pytest.mark.parametrize('sequence_type, constructor_arg, length', [
        (_IterCountingSet, {10}, 1),
        (_IterCountingSet, {10, 20}, 2),
        (_IterCountingSet, {10, 20, 30}, 3),
        (_IterCountingSet, set(range(1000)), 1000),
        (_IterCountingDict, {'a': 1}, 1),
        (_IterCountingDict, {'a': 1, 'b': 2}, 2),
        (_IterCountingDict, {'a': 1, 'b': 2, 'c': 3}, 3),
        (_IterCountingDict, {range(n): n for n in range(1000)}, 1000),
    ])
    def test_nonempty_sized_nonsequence_works_without_iter(self, subtests,
                                                           sequence_type,
                                                           constructor_arg,
                                                           length):
        """__iter__ is not called on a nonempty non-sequence supporting len."""
        sized = sequence_type(constructor_arg)
        result = gencomp1.length_of_opt(sized)
        with subtests.test('Result should be correct'):
            assert result == length
        with subtests.test('__iter__ should not be called'):
            assert sized.iter_calls == 0

    def test_long_sequence_length_is_found(self):
        """
        A length is found, where it would be very slow if done via __iter__.

        This fairly effectively tests if the len builtin is used.
        """
        result = gencomp1.length_of_opt(range(2_000_000_000))
        assert result == 2_000_000_000

    def test_many_long_sequence_lengths_are_found(self):
        """
        Lengths are found, where it would not all finish if done via __iter__.

        This effectively tests if the len builtin is used. The reason it is
        done by repeatedly checking lengths, rather than getting a length of
        something extremely large, is that len is not permitted to return a
        value that doesn't fit in a machine word, so a sufficiently great
        length (even on a range object, where it takes O(1) space) would fail
        with TypeError.
        """
        results = (gencomp1.length_of_opt(range(2_000_000_000))
                   for _ in range(100_000))

        assert set(results) == {2_000_000_000}

    def test_iter_called_once_if_len_is_not_supported(self, subtests):
        """
        Finding the length of a non-sized iterable calls __iter__ once.

        The details of this test method may be compared to
        TestTailOpt.test_iter_called_once_on_nonsequence.
        """
        sequence = _IterCountingList([10, 20, 30, 40])
        indirect_iterator = itertools.chain(sequence)

        if sequence.iter_calls != 0:
            raise Exception("itertools.chain shouldn't call __iter__ eagerly")

        result = gencomp1.length_of_opt(indirect_iterator)

        with subtests.test('Result should be correct'):
            assert result == 4

        with subtests.test('__iter__ should be called once'):
            assert sequence.iter_calls == 1


class TestHowMany:
    """
    Tests for the how_many function.

    Methods in this class may be compared to methods in TestMyFilter.
    """

    __slots__ = ()

    def test_none_satisfying_is_zero_from_sequence(self):
        """When no items satisfy the predicate, the count is zero."""
        sequence = (0, 1, 2)
        result = gencomp1.how_many(lambda n: n < 0, sequence)
        assert result == 0

    def test_none_satisfying_is_zero_from_iterator(self):
        """When no items satisfy the predicate, the count is zero."""
        iterator = iter((0, 1, 2))
        result = gencomp1.how_many(lambda n: n < 0, iterator)
        assert result == 0

    def test_none_satisfying_is_zero_from_big_set(self):
        """When no items from a big set satisfy, the count is zero."""
        obj = object()
        items = {object() for _ in range(100_000)}
        result = gencomp1.how_many(lambda item: item == obj, items)
        assert result == 0

    def test_none_satisfying_is_zero_from_long_iterator(self):
        """When no items from a long generator satisfy, the count is zero."""
        obj = object()
        iterator = (object() for _ in range(100_000))
        result = gencomp1.how_many(lambda item: item == obj, iterator)
        assert result == 0

    def test_some_but_not_last_satisfying_counts_them_from_sequence(self):
        """When some but not the last satisfy, those that do are counted."""
        sequence = range(1, 12)
        result = gencomp1.how_many(lambda n: n % 3 == 0, sequence)
        assert result == 3

    def test_some_but_not_last_satisfying_counts_them_from_iterator(self):
        """When some but not the last satisfy, those that do are counted."""
        iterator = iter(range(1, 12))
        result = gencomp1.how_many(lambda n: n % 3 == 0, iterator)
        assert result == 3

    def test_some_including_last_satisfying_counts_them_from_sequence_1(self):
        """When some including the last satisfy, those that do are counted."""
        sequence = range(1, 13)
        result = gencomp1.how_many(lambda n: n % 3 == 0, sequence)
        assert result == 4

    def test_some_including_last_satisfying_counts_them_from_iterator_1(self):
        """When some including the last satisfy, those that do are counted."""
        iterator = iter(range(1, 13))
        result = gencomp1.how_many(lambda n: n % 3 == 0, iterator)
        assert result == 4

    def test_some_including_last_satisfying_counts_them_from_sequence_2(self):
        """When some from a list satisfy, those that do are counted."""
        sequence = [t * 2 for t in ['a', 'bc', 'de', 'f', 'ghi', 'jk']]
        result = gencomp1.how_many(lambda s: len(s) == 4, sequence)
        assert result == 3

    def test_some_including_last_satisfying_counts_them_from_iterator_2(self):
        """When some from a generator satisfy, those that do are counted."""
        iterator = (t * 2 for t in ['a', 'bc', 'de', 'f', 'ghi', 'jk'])
        result = gencomp1.how_many(lambda s: len(s) == 4, iterator)
        assert result == 3

    def test_none_predicate_counts_truthy_from_sequence(self):
        """A predicate of None checks items themselves, counts truthy ones."""
        sequence = [(), [], '', 'a', {}, set(), [0], None]
        result = gencomp1.how_many(None, sequence)
        assert result == 2

    def test_none_predicate_counts_truthy_from_iterator(self):
        """A predicate of None checks items themselves, counts truthy ones."""
        iterator = iter([(), [], '', 'a', {}, set(), [0], None])
        result = gencomp1.how_many(None, iterator)
        assert result == 2

    def test_none_predicate_counts_truthy_from_big_sequence(self):
        """A predicate of None counts truthy items, even in a long sequence."""
        sequence = [0, 1] * 50_000
        result = gencomp1.how_many(None, sequence)
        assert result == 50_000

    def test_none_predicate_counts_truthy_from_big_iterator(self):
        """A predicate of None counts truthy items, even in a long iterator."""
        iterator = iter([0, 1] * 50_000)
        result = gencomp1.how_many(None, iterator)
        assert result == 50_000

    def test_none_predicate_counts_truthy_even_if_none_from_sequence(self):
        """A predicate of None counts zero if all items are falsy."""
        sequence = [[], (), {}, set()]
        result = gencomp1.how_many(None, sequence)
        assert result == 0

    def test_none_predicate_counts_truthy_even_if_none_from_iterator(self):
        """A predicate of None counts zero if all items are falsy."""
        iterator = iter([[], (), {}, set()])
        result = gencomp1.how_many(None, iterator)
        assert result == 0

    def test_none_predicate_counts_truthy_even_if_all_from_sequence(self):
        """A predicate of None counts all items if none are falsy."""
        sequence = ['hello', 'glorious', 'world']
        result = gencomp1.how_many(None, sequence)
        assert result == 3

    def test_none_predicate_counts_truthy_even_if_all_from_iterator(self):
        """A predicate of None counts all items if none are falsy."""
        iterator = iter(['hello', 'glorious', 'world'])
        result = gencomp1.how_many(None, iterator)
        assert result == 3


@pytest.fixture(name='scrambled_dicts', params=[  # Parametrized by PRNG seed.
    260429228478576778,
    9502498993413641577,
    11272998565121818203,
])
def fixture_scrambled_dicts(request):
    """Make a shuffled 40,000-item injective dict and its inverse."""
    rand = random.Random(request.param)
    elements = range(-20_000, 20_000)
    keys = list(elements)
    rand.shuffle(keys)
    values = list(elements)
    rand.shuffle(values)
    return dict(zip(keys, values)), dict(zip(values, keys))


@pytest.mark.parametrize('implementation', [
    gencomp1.invert,
    gencomp1.invert_alt,
])
class TestInvert:
    """Tests for the invert and invert_alt functions."""

    __slots__ = ()

    def test_empty_inverts_empty(self, implementation):
        """The inverse of an empty dict is an empty dict."""
        assert implementation({}) == {}

    def test_small_injective_inverse_flips_keys_values(self, implementation):
        """A small injective (k, v) dict inverts to the (v, k) dict."""
        preimage = {'a': 10, 'b': 20, 'cd': 30, 'efg': 40}
        expected = {10: 'a', 20: 'b', 30: 'cd', 40: 'efg'}
        assert implementation(preimage) == expected

    def test_small_injective_inverse_keeps_order(self, implementation):
        """A small injective (k, v) dict inverts to same-order (v, k)s."""
        preimage = {'a': 10, 'b': 20, 'cd': 30, 'efg': 40}
        expected = [(10, 'a'), (20, 'b'), (30, 'cd'), (40, 'efg')]
        result = implementation(preimage)
        assert list(result.items()) == expected

    def test_small_injective_inverse_is_involution(self, implementation):
        """A small injective dict is equal to its inverse's inverse."""
        preimage = {'a': 10, 'b': 20, 'cd': 30, 'efg': 40}
        assert implementation(implementation(preimage)) == preimage

    def test_small_injective_inverse_inverse_keeps_order(self, implementation):
        """A small injective dict's inverse's inverse's has the same order."""
        preimage = {'a': 10, 'b': 20, 'cd': 30, 'efg': 40}
        expected = [('a', 10), ('b', 20), ('cd', 30), ('efg', 40)]
        result = implementation(implementation(preimage))
        assert list(result.items()) == expected

    def test_big_injective_inverse_flips_keys_values(self, implementation):
        """A big injective (k, v) dict inverts to the (v, k) dict."""
        preimage = {n: n**2 for n in range(40_000)}
        expected = {n**2: n for n in range(40_000)}
        assert implementation(preimage) == expected

    def test_big_injective_inverse_keeps_order(self, implementation):
        """A big injective (k, v) dict inverts to same-order (v, k)s."""
        preimage = {n: n**2 for n in range(40_000)}
        expected = [(n**2, n) for n in range(40_000)]
        result = implementation(preimage)
        assert list(result.items()) == expected

    def test_big_injective_inverse_is_involution(self, implementation):
        """A big injective dict is equal to its inverse's inverse."""
        preimage = {n: n**2 for n in range(40_000)}
        assert implementation(implementation(preimage)) == preimage

    def test_big_injective_inverse_inverse_keeps_order(self, implementation):
        """A big injective dict's inverse's inverse's has the same order."""
        preimage = {n: n**2 for n in range(40_000)}
        expected = [(n, n**2) for n in range(40_000)]
        result = implementation(implementation(preimage))
        assert list(result.items()) == expected

    def test_random_injective_inverse_flips_keys_values(self, scrambled_dicts,
                                                        implementation):
        """A big random injective (k, v) dict inverts to the (v, k) dict."""
        preimage, expected = scrambled_dicts
        assert implementation(preimage) == expected

    def test_random_injective_inverse_keeps_order(self, scrambled_dicts,
                                                  implementation):
        """A big random injective (k, v) dict inverts to same-order (v, k)s."""
        preimage, expected_inverse = scrambled_dicts
        result = implementation(preimage)
        assert list(result.items()) == list(expected_inverse.items())

    def test_random_injective_inverse_is_involution(self, scrambled_dicts,
                                                    implementation):
        """A big random injective dict is equal to its inverse's inverse."""
        preimage, _ = scrambled_dicts
        assert implementation(implementation(preimage)) == preimage

    def test_random_injective_inverse_inverse_keeps_order(self,
                                                          scrambled_dicts,
                                                          implementation):
        """
        A big random injective dict's inverse's inverse has the same order.
        """
        preimage, _ = scrambled_dicts
        result = implementation(implementation(preimage))
        assert list(result.items()) == list(preimage.items())

    def test_small_identity_inverts_equal(self, implementation):
        """A small dict taking elements to themselves inverts to itself."""
        preimage = {ch: ch for ch in string.ascii_lowercase}
        assert implementation(preimage) == preimage

    def test_small_identity_inverse_keeps_order(self, implementation):
        """A small dict taking elements to themselves inverts in same order."""
        preimage = {ch: ch for ch in string.ascii_lowercase}
        expected = [(ch, ch) for ch in string.ascii_lowercase]
        result = implementation(preimage)
        assert list(result.items()) == expected

    def test_big_identity_inverts_equal(self, implementation):
        """A big dict taking elements to themselves inverts to itself."""
        preimage = {n: n for n in range(40_000)}
        assert implementation(preimage) == preimage

    def test_big_identity_inverse_keeps_order(self, implementation):
        """A big dict taking elements to themselves inverts in same order."""
        preimage = {n: n for n in range(40_000)}
        expected = [(n, n) for n in range(40_000)]
        result = implementation(preimage)
        assert list(result.items()) == expected

    # FIXME: Add non-injective dict tests of overwriting and ordering behavior.


# FIXME: The (currently 14) gencomp1.distinct* functions, and the (currently 3)
#        gencomp1.Distinct* classes, still need pytest tests.


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
