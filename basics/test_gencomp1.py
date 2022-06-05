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
        it = implementation('pqr', n)
        assert list(it) == expected

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
])
class TestDrop(CommonIteratorTests):
    """Tests for the drop_good and drop functions."""

    __slots__ = ()

    def instantiate(self, implementation):
        return implementation(range(5), 2)

    def test_dropping_none_from_empty_is_empty(self, implementation):
        """Dropping no items when there are no items yields no items."""
        it = implementation(range(0), 0)
        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_dropping_some_from_empty_is_empty(self, implementation, n):
        """
        Dropping some items when there are none yields none (without error).
        """
        it = implementation(range(0), n)
        with pytest.raises(StopIteration):
            next(it)

    def test_dropping_none_from_nonempty_gives_all(self, implementation):
        """Dropping no items when there are some items yields all the items."""
        it = implementation(range(5), 0)
        assert list(it) == [0, 1, 2, 3, 4]

    @pytest.mark.parametrize('n, expected', [
        (1, [1, 2, 3, 4]),
        (2, [2, 3, 4]),
        (3, [3, 4]),
        (4, [4]),
    ])
    def test_dropping_some_from_nonempty_gives_suffix(self, implementation,
                                                      n, expected):
        """Dropping some items when there are some items yields the rest."""
        it = implementation(range(5), n)
        assert list(it) == expected

    def test_dropping_all_from_nonempty_is_empty(self, implementation):
        """Dropping all items when there are some items yields no items."""
        it = implementation(range(5), 5)
        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize('n', [6, 7, 15, 100, 1_000_000])
    def test_dropping_extra_from_nonempty_is_empty(self, implementation, n):
        """Dropping more than all items yields no items (without error)."""
        it = implementation(range(5), n)
        with pytest.raises(StopIteration):
            next(it)

    def test_dropping_some_from_infinite_gives_rest(self, implementation):
        """
        Dropping some items when there are infinitely many yields the rest.
        """
        it = implementation(itertools.count(1), 1000)
        prefix_of_suffix = itertools.islice(it, 6)
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
        it = implementation('pqr', n)
        assert list(it) == expected


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

    def test_empty_suffix_of_empty_is_empty(self, implementation):
        """No items taken from the end of no items are no items."""
        assert implementation([], 0) == ()

    @pytest.mark.parametrize('n', [1, 2, 10, 100, 1_000_000])
    def test_all_suffixes_of_empty_are_empty(self, implementation, n):
        """Trying to take some items from the end of no items gets no items."""
        assert implementation([], n) == ()

    def test_empty_suffix_of_nonempty_is_empty(self, implementation):
        """No items taken from the end of some items are no items."""
        iterable = (x**2 for x in range(100))
        assert implementation(iterable, 0) == ()

    @pytest.mark.parametrize('n, expected', [
        (1, (9801,)),
        (2, (9604, 9801)),
        (3, (9409, 9604, 9801)),
        (4, (9216, 9409, 9604, 9801)),
        (5, (9025, 9216, 9409, 9604, 9801)),
    ])
    def test_short_suffix_of_long_is_full_short(self, implementation,
                                                n, expected):
        """Taking a few items from end of many items gets those few items."""
        iterable = (x**2 for x in range(100))
        assert implementation(iterable, n) == expected


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


class _IterCountingList(list):
    """A list that counts how many times __iter__ is called on it."""

    __slots__ = ('iter_calls',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter_calls = 0

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    def __iter__(self):
        self.iter_calls += 1
        return super().__iter__()


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


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
