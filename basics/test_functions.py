#!/usr/bin/env python

"""Tests for the functions in functions.py."""

from collections.abc import Iterator
import functools
import io
import itertools
import sys
import unittest

from parameterized import parameterized, parameterized_class

import fibonacci
import functions
import recursion

_original_count_tree_nodes = functions.count_tree_nodes


@functools.cache
def _fib5k():
    """Return a list of the first 5000 Fibonacci numbers, read from a file."""
    with open('fib5k.txt', encoding='utf-8') as file:
        return list(map(int, file))


# TODO: Replace this with a parameterized-decorator factory (so it will be a
# decorator factory factory) that takes a module name and returns a decorator
# factory that takes a variable number of implementation name arguments and
# behaves like @parameterized.parameterized_class as used in the tests below.
# Write tests for it, and also use it instead of @parameterized_class below.
#
# If you name it make_implementation_parameterizer, usage will look like:
#
#     for_implementations = make_implementation_parameterizer(functions)
#
#     @for_implementations('make_counter', 'make_counter_alt')
#     class TestMakeCounter(unittest.TestCase):
#         ...
#
#     @for_implementations('make_next_fibonacci', 'make_next_fibonacci_alt')
#     class TestMakeNextFibonacci(unittest.TestCase):
#         ...
#
# The parameterized decorator (like for_implementations in the above example)
# returned by the decorator factory factory should accept arbitrarily many
# positional arguments representing names of entities to test.
class _NamedImplementationTestCase(unittest.TestCase):
    """
    Base class to test entities in the functions module by their names.

    The recommended use is to inherit from this class and assign an unqualified
    attribute name (most often a function name) to the implementation_name
    class attribute by using the @parameterized.parameterized_class decorator.
    """

    __slots__ = ()

    @property
    def implementation(self):
        """The function being tested."""
        return getattr(functions, self.implementation_name)


@parameterized_class(('implementation_name',), [
    ('make_counter',),
    ('make_counter_alt',),
])
class TestMakeCounter(_NamedImplementationTestCase):
    """Tests for the make_counter and make_counter_alt functions."""

    __slots__ = ()

    def test_starts_at_zero_with_no_start_argument(self):
        f = self.implementation()
        self.assertEqual(f(), 0)

    def test_starts_at_start_argument_value_if_passed(self):
        f = self.implementation(76)
        self.assertEqual(f(), 76)

    def test_calls_count_up_from_zero_without_start(self):
        expected_list = list(range(1000))
        f = self.implementation()
        results = [f() for _ in range(1000)]
        self.assertListEqual(results, expected_list)

    @parameterized.expand([
        ('start_0', 0, range(0, 1000)),
        ('start_1', 1, range(1, 1001)),
        ('start_500', 500, range(500, 1500)),
        ('start_neg_342', -342, range(-342, 658)),
    ])
    def test_calls_count_up_from_start(self, _name, start, expected):
        expected_list = list(expected)
        f = self.implementation(start)
        results = [f() for _ in range(1000)]
        self.assertListEqual(results, expected_list)


    def test_calls_to_separate_counters_count_independently(self):
        f = self.implementation()
        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)

        g = self.implementation()
        self.assertEqual(f(), 2)
        self.assertEqual(g(), 0)
        self.assertEqual(f(), 3)
        self.assertEqual(g(), 1)
        self.assertEqual(g(), 2)

        h = self.implementation(10)
        self.assertEqual(h(), 10)
        self.assertEqual(f(), 4)
        self.assertEqual(g(), 3)
        self.assertEqual(h(), 11)
        self.assertEqual(g(), 4)
        self.assertEqual(h(), 12)
        self.assertEqual(h(), 13)
        self.assertEqual(g(), 5)
        self.assertEqual(g(), 6)
        self.assertEqual(f(), 5)
        self.assertEqual(h(), 14)


@parameterized_class(('implementation_name',), [
    ('make_next_fibonacci',),
    ('make_next_fibonacci_alt',),
])
class TestMakeNextFibonacci(_NamedImplementationTestCase):
    """
    Tests for the make_next_fibonacci and make_next_fibonacci_alt functions.
    """

    __slots__ = ()

    def test_successive_fibonacci_numbers_are_returned(self):
        expected = _fib5k()
        f = self.implementation()
        actual = [f() for _ in range(5000)]
        self.assertListEqual(actual, expected)

    def test_calls_to_separate_functions_compute_independently(self):
        f = self.implementation()
        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 2)
        self.assertEqual(f(), 3)

        g = self.implementation()
        self.assertEqual(g(), 0)
        self.assertEqual(f(), 5)
        self.assertEqual(g(), 1)
        self.assertEqual(f(), 8)
        self.assertEqual(g(), 1)
        self.assertEqual(f(), 13)
        self.assertEqual(g(), 2)
        self.assertEqual(f(), 21)
        self.assertEqual(g(), 3)
        self.assertEqual(f(), 34)

        self.assertEqual(f(), 55)
        self.assertEqual(f(), 89)
        self.assertEqual(g(), 5)


class TestAsFunc(unittest.TestCase):
    """Tests for the as_func function."""

    __slots__ = ()

    @parameterized.expand([
        ('range', range(3)),
        ('range_iterator', iter(range(3))),
        ('list', [0, 1, 2]),
        ('list_iterator', iter([0, 1, 2])),
        ('generator', (x for x in (0, 1, 2))),
    ])
    def test_returned_function_calls_next_on_iterable(self, _name, iterable):
        f = functions.as_func(iterable)

        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 2)

        with self.assertRaises(StopIteration):
            f()

    def test_calls_to_separate_functions_iterate_independently(self):
        f = functions.as_func([10, 20, 30])
        self.assertEqual(f(), 10)
        self.assertEqual(f(), 20)

        g = functions.as_func(x**2 for x in itertools.count(2))
        self.assertEqual(f(), 30)
        self.assertEqual(g(), 4)
        with self.assertRaises(StopIteration):
            f()

        self.assertEqual(g(), 9)
        self.assertEqual(g(), 16)


@parameterized_class(('implementation_name',), [
    ('as_iterator_limited',),
    ('as_iterator_limited_alt',),
])
class TestAsIteratorLimited(_NamedImplementationTestCase):
    """
    Tests for the as_iterator_limited and as_iterator_limited_alt functions.
    """

    __slots__ = ()

    def test_iterator_calls_simple_f_until_sentinel(self):
        d = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e'}
        k = 'a'

        def f():
            nonlocal k
            k = d[k]
            return k

        it = self.implementation(f, 'd')
        self.assertEqual(next(it), 'b')
        self.assertEqual(next(it), 'c')
        with self.assertRaises(StopIteration):
            next(it)

    @parameterized.expand([
        ('make_counter', 2000, list(range(2000))),
        ('make_counter_alt', 2000, list(range(2000))),
        ('make_next_fibonacci', 89, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
        ('make_next_fibonacci_alt', 89, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
    ])
    def test_iterator_calls_f_until_sentinel(self, f_name, sentinel, expected):
        """
        Iterators on synthesized iterator-like functions "round trip."

        Calling as_iterator_limited{_alt} on synthesized functions that
        themselves behave like calling next() on an iterator behaves as
        expected.
        """
        f_impl = getattr(functions, f_name)
        it = self.implementation(f_impl(), sentinel)
        self.assertIsInstance(it, Iterator)
        self.assertListEqual(list(it), expected)


@parameterized_class(('implementation_name',), [
    ('as_iterator',),
    ('as_iterator_alt',),
])
class TestAsIteratorLimited(_NamedImplementationTestCase):
    """Tests for the as_iterator and as_iterator_alt functions."""

    __slots__ = ()

    def test_iterator_calls_simple_f(self):
        d = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e', 'e': 'a'}
        k = 'a'

        def f():
            nonlocal k
            k = d[k]
            return k

        it = self.implementation(f)
        self.assertIsInstance(it, Iterator)
        prefix = list(itertools.islice(it, 12))
        self.assertListEqual(prefix, list('bcdeabcdeabc'))

    @parameterized.expand([
        ('make_counter', 2000, list(range(2000))),
        ('make_counter_alt', 2000, list(range(2000))),
        ('make_next_fibonacci', 11, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
        ('make_next_fibonacci_alt', 11, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
    ])
    def test_iterator_calls_f(self, f_name, prefix_length, expected):
        f_impl = getattr(functions, f_name)

        it = self.implementation(f_impl())
        self.assertIsInstance(it, Iterator)

        prefix = list(itertools.islice(it, prefix_length))
        self.assertListEqual(prefix, expected)


@parameterized_class(('implementation_name',), [
    ('count_tree_nodes',),
    ('count_tree_nodes_alt',),
])
class TestCountTreeNodes(_NamedImplementationTestCase):
    """Tests for the count_tree_nodes and count_tree_nodes_alt functions."""

    __slots__ = ()

    def test_str_has_one_node(self):
        """Strings (like other non-tuple iterables) are taken as leaves."""
        root = 'a parrot'
        result = self.implementation(root)
        self.assertEqual(result, 1)

    def test_empty_tuple_has_one_node(self):
        """An empty tuple is taken as a leaf."""
        root = ()
        result = self.implementation(root)
        self.assertEqual(result, 1)

    def test_small_nontrivial_nested_tuple_of_ints_is_fully_traversed(self):
        """A nested tuple of varying depth has its internal and leaf nodes."""
        root = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
        result = self.implementation(root)
        self.assertEqual(result, 22)

    def test_list_containing_nontrivial_nested_tuple_has_only_one_node(self):
        """A list, even of tuple(s), is taken as a leaf (so not traversed)."""
        root = [((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))]
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @parameterized.expand([
        ('n_equals_0', 0, 1),
        ('n_equals_1', 1, 1),
        ('n_equals_2', 2, 3),
        ('n_equals_3', 3, 5),
        ('n_equals_4', 4, 9),
        ('n_equals_5', 5, 15),
        ('n_equals_6', 6, 25),
        ('n_equals_7', 7, 41),
        ('n_equals_8', 8, 67),
        ('n_equals_9', 9, 109),
        ('n_equals_10', 10, 177),
        ('n_equals_11', 11, 287),
        ('n_equals_12', 12, 465),
        ('n_equals_13', 13, 753),
        ('n_equals_14', 14, 1219),
        ('n_equals_15', 15, 1973),
        ('n_equals_16', 16, 3193),
    ])
    def test_fibonacci_structure_is_fully_traversed(self, _name, n, expected):
        """Structures of Fibonacci subproblems have internal and leaf nodes."""
        root = fibonacci.fib_nest(n)
        result = self.implementation(root)
        self.assertEqual(result, expected)


# TODO: If reused, extract the stdout-redirecting fixture to its own class.
class TestCountTreeNodesInstrumented(unittest.TestCase):
    """Tests for the count_tree_nodes_instrumented function."""

    __slots__ = ('_old_stdout', '_stdout')

    def setUp(self):
        """Monkeypatch ("redirect") standard output to capture it for tests."""
        self._old_stdout = sys.stdout
        self._stdout = sys.stdout = io.StringIO()

    def tearDown(self):
        """Restore standard output."""
        sys.stdout = self._old_stdout

    # TODO: Add para to docstring explaining why this test does so many things.
    def test_function_patched_and_restored_when_no_exception_is_raised(self):
        """count_tree_nodes is patched/unpatched in the absence of errors."""
        # TODO: Should this force an "error" status rather than mere "failure"?
        self.assertIs(functions.count_tree_nodes, _original_count_tree_nodes,
            "count_tree_nodes was ALREADY wrong at the START of the test")

        root = recursion.make_deep_tuple(2)
        result = functions.count_tree_nodes_instrumented(root)
        output = self._out

        self.assertEqual(result, 3)

        self.assertEqual(output, 'count_tree_nodes(()) -> 1\n'
                                 'count_tree_nodes(((),)) -> 2\n'
                                 'count_tree_nodes((((),),)) -> 3\n')

        self.assertIs(functions.count_tree_nodes, _original_count_tree_nodes,
            "count_tree_nodes_instrumented failed to restore count_tree_nodes")

        # FIXME: Call count_tree_nodes and show the behavior is also restored.


    @property
    def _out(self):
        """The text sent so far to stdout during a single test."""
        return self._stdout.getvalue()


if __name__ == '__main__':
    unittest.main()
