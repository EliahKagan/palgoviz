#!/usr/bin/env python

"""
Some recursion examples (and a few related iterative implementations).

See also object_graph.py.

NOTE: Where not otherwise specified, functions that process a single sequence
or other iterable (e.g., values), and that are documented with a time or space
complexity containing the variable n, use it to mean the number of items in the
input (so if the argument is values, then n == len(values)).
"""

import bisect
import collections
import contextlib
import functools
import math
import operator
import random
import secrets

import decorators
import queues


def countdown(n):
    """
    Count down from n, printing the positive numbers, one per line.

    >>> countdown(10)
    10
    9
    8
    7
    6
    5
    4
    3
    2
    1
    >>> countdown(-1)
    Traceback (most recent call last):
      ...
    ValueError: -1 is less than 0
    """
    if n < 0:
        raise ValueError(f'{n} is less than 0')
    if n == 0:
        return
    print(n)
    countdown(n-1)


def semifactorial(n):
    """
    Compute the semifactorial ("double factorial") of n, by simple recursion.

    Semifactorials, like factorials, are products of positive integers, but
    they skip every other term. For odd (resp. even) n, the semifactorial,
    written n!!, is the product of all positive odd (resp. even) integers less
    than or equal to n. That is:

        n!! = n * (n - 2) * (n - 4) * (n - 6) * ...

    where the last term is 2 or 1. (Like 0!, 0!! is the empty product.)

    This is a simple recursive implementation. This and the other semifactorial
    implementations below it may all assume n is a nonnegative int.

    >>> [semifactorial(n) for n in range(15)]
    [1, 1, 2, 3, 8, 15, 48, 105, 384, 945, 3840, 10395, 46080, 135135, 645120]
    """
    return 1 if n < 2 else n * semifactorial(n - 2)


def semifactorial_tail(n):
    """
    Compute the semifactorial ("double factorial") of n, by tail recursion.

    See tail_calls.ipynb.

    Note that Python does not have proper tail calls, and CPython does not
    eliminate or optimize tail calls in even the simplest tail-recursive
    functions.

    >>> [semifactorial_tail(n) for n in range(15)]
    [1, 1, 2, 3, 8, 15, 48, 105, 384, 945, 3840, 10395, 46080, 135135, 645120]
    """
    def semifac(acc, k):
        return acc if k < 2 else semifac(acc * k, k - 2)

    return semifac(1, n)


def semifactorial_iterative(n):
    """
    Compute the semifactorial ("double factorial") of n by explicit iteration.

    This implementation uses the iterative accumulator pattern. This could be
    done with either a for loop or a while loop. To clarify the conceptual
    connection to semifactorial_tail, a while loop is used.

    >>> [semifactorial_iterative(n) for n in range(15)]
    [1, 1, 2, 3, 8, 15, 48, 105, 384, 945, 3840, 10395, 46080, 135135, 645120]
    """
    acc = 1
    while n > 1:
        acc *= n
        n -= 2
    return acc


def semifactorial_good(n):
    """
    Compute the semifactorial ("double factorial") of n via math.prod.

    This implementation uses no recursion and no loops or comprehensions. (It
    fits easily on one line.)

    >>> [semifactorial_good(n) for n in range(15)]
    [1, 1, 2, 3, 8, 15, 48, 105, 384, 945, 3840, 10395, 46080, 135135, 645120]
    """
    return math.prod(range(n, 1, -2))


def semifactorial_reduce(n):
    """
    Compute the semifactorial ("double factorial") of n via functools.reduce.

    This implementation uses no recursion and no loops or comprehensions. (It
    fits easily on one line.) This was the best way do do it prior to Python
    3.8 when math.prod was added.

    >>> [semifactorial_reduce(n) for n in range(15)]
    [1, 1, 2, 3, 8, 15, 48, 105, 384, 945, 3840, 10395, 46080, 135135, 645120]
    """
    return functools.reduce(operator.mul, range(n, 1, -2), 1)


def add_all_iterative(values):
    """
    Add all the numbers. Like sum(values).

    Assumes values is a sequence (e.g., it can be indexed) of numbers.

    >>> add_all_iterative([])
    0
    >>> add_all_iterative([7])
    7
    >>> add_all_iterative((3, 6, 1))
    10
    """
    result = 0
    for x in values:
        result += x
    return result


def add_all_slow(values):
    """
    Add all the numbers recursively. Like sum(values). values is not modified.

    Assumes values is a sequence (e.g., it can be indexed) of numbers.
    >>> add_all_slow(())
    0
    >>> add_all_slow([])
    0
    >>> add_all_slow([7])
    7
    >>> add_all_slow((3, 6, 1))
    10
    >>> values = [2,3,5]
    >>> add_all_slow(values)
    10
    >>> values
    [2, 3, 5]
    """
    match values:
        case []:
            return 0
        case [num, *rest]:
            return num + add_all_slow(rest)


def add_all(values):
    """
    Add all the numbers recursively. Like sum(values). values is not modified.

    Assumes values is a sequence (e.g., it can be indexed) of numbers.
    >>> add_all(())
    0
    >>> add_all([])
    0
    >>> add_all([7])
    7
    >>> add_all((3, 6, 1))
    10
    >>> values = [2, 3, 5]
    >>> add_all(values)
    10
    >>> values
    [2, 3, 5]
    """
    def add_from(index):
        if index == len(values):
            return 0
        return values[index] + add_from(index + 1)

    return add_from(0)


def linear_search_good(values, x):
    """
    Return an index to some occurrence of x in values, if any.

    If there is no such occurrence, None is returned.

    >>> linear_search_good([], 9)
    >>> linear_search_good([2, 3], 2)
    0
    >>> linear_search_good((4, 5, 6), 5)
    1
    >>> linear_search_good([3, 1, 2, 8, 6, 5, 7], 8)
    3
    """
    try:
        return values.index(x)
    except ValueError:
        return None


def linear_search_iterative(values, x):
    """
    Return an index to some occurrence of x in values, if any.

    If there is no such occurrence, None is returned.

    >>> linear_search_iterative([], 9)
    >>> linear_search_iterative([2, 3], 2)
    0
    >>> linear_search_iterative((4, 5, 6), 5)
    1
    >>> linear_search_iterative([3, 1, 2, 8, 6, 5, 7], 8)
    3
    """
    for index, value in enumerate(values):
        if value == x:
            return index
    return None


def linear_search(values, x):
    """
    Return an index to some occurrence of x in values, if any.

    If there is no such occurrence, None is returned.

    >>> linear_search([], 9)
    >>> linear_search([2, 3], 2)
    0
    >>> linear_search((4, 5, 6), 5)
    1
    >>> linear_search([3, 1, 2, 8, 6, 5, 7], 8)
    3
    """
    def search_from(index):
        if index == len(values):
            return None
        if values[index] == x:
            return index
        return search_from(index + 1)

    return search_from(0)


def binary_search(values, x):
    """
    Return an index to some occurrence of x in values, which is sorted.

    If there is no such occurrence, None is returned.

    >>> binary_search([], 9)
    >>> binary_search([2, 3], 2)
    0
    >>> binary_search((4, 5, 6), 5)
    1
    >>> binary_search((4, 5, 6), 7)
    >>> binary_search([1, 2, 3, 5, 6, 7, 8], 3)
    2
    >>> binary_search([10], 10)
    0
    >>> binary_search([10, 20], 10)
    0
    >>> binary_search([10, 20], 20)
    1
    >>> binary_search([10, 20], 15)
    >>>
    """
    def help_binary(low, high):  # high is an inclusive endpoint.
        if low > high:
            return None
        halfway = (low + high) // 2
        if x > values[halfway]:
            return help_binary(halfway + 1, high)
        if x < values[halfway]:
            return help_binary(low, halfway - 1)
        return halfway  # values[halfway] should = x, possibly add assert.

    return help_binary(0, len(values) - 1)


def binary_search_iterative(values, x):
    """
    Return an index to some occurrence of x in values, which is sorted.

    If there is no such occurrence, None is returned.

    >>> binary_search_iterative([], 9)
    >>> binary_search_iterative([2, 3], 2)
    0
    >>> binary_search_iterative((4, 5, 6), 5)
    1
    >>> binary_search_iterative((4, 5, 6), 7)
    >>> binary_search_iterative([1, 2, 3, 5, 6, 7, 8], 3)
    2
    >>> binary_search_iterative([10], 10)
    0
    >>> binary_search_iterative([10, 20], 10)
    0
    >>> binary_search_iterative([10, 20], 20)
    1
    >>> binary_search_iterative([10, 20], 15)
    >>>
    """
    low = 0
    high = len(values) - 1

    while low <= high:
        halfway = (low + high) // 2
        if x > values[halfway]:
            low = halfway + 1
        elif x < values[halfway]:
            high = halfway - 1
        else:  # values[halfway] should = x, possibly add assert.
            return halfway

    return None


def binary_search_good(values, x):
    """
    Return an index to some occurrence of x in values, which is sorted.

    If there is no such occurrence, None is returned.

    >>> binary_search_good([], 9)
    >>> binary_search_good([2, 3], 2)
    0
    >>> binary_search_good((4, 5, 6), 5)
    1
    >>> binary_search_good((4, 5, 6), 7)
    >>> binary_search_good([1, 2, 3, 5, 6, 7, 8], 3)
    2
    >>> binary_search_good([10], 10)
    0
    >>> binary_search_good([10, 20], 10)
    0
    >>> binary_search_good([10, 20], 20)
    1
    >>> binary_search_good([10, 20], 15)
    >>>
    """
    index = bisect.bisect_left(values,x)
    return index if (index < len(values)) and (values[index] == x) else None


def binary_insertion_sort(values):
    """
    Iterative stable binary insertion sort, creating a new list.

    The input is not modified. The output list starts empty. It remains sorted
    after each insertion. This algorithm is adaptive: the closer to sorted its
    input already is, the less work it has to do. The insertion point is found
    by binary search, which is what makes this *binary* insertion sort.

    Search and insertion may be performed using a standard library facility.

    The worst time complexity is O(N^2). Best case scenerio inserstion is just
    an append but search is still log(N), thus O(Nlog(N)). Average time
    complexity over all possible inputs will be O(N^2) because on average we
    will have to move half the elements O(cN) = O(N).

    >>> binary_insertion_sort([])
    []
    >>> binary_insertion_sort(())
    []
    >>> binary_insertion_sort((2,))
    [2]
    >>> binary_insertion_sort([10, 20])
    [10, 20]
    >>> binary_insertion_sort([20, 10])
    [10, 20]
    >>> binary_insertion_sort([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> binary_insertion_sort(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> binary_insertion_sort(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> binary_insertion_sort([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    output = []
    for element in values:
        bisect.insort_right(output, element)
    return output


def binary_insertion_sort_recursive(values):
    """
    Recursive stable binary insertion sort, creating a new list.

    See the description of binary_insertion_sort above. (There is little reason
    to implement this recursively in Python, except as an exercise, and for
    conceptual clarity.) Ensure the best, average, and worst-case asymptotic
    time complexities are the same as in binary_insertion_sort; avoid incurring
    asymptotically worse performance from copying. Assume values is a sequence.

    >>> binary_insertion_sort_recursive([])
    []
    >>> binary_insertion_sort_recursive(())
    []
    >>> binary_insertion_sort_recursive((2,))
    [2]
    >>> binary_insertion_sort_recursive([10, 20])
    [10, 20]
    >>> binary_insertion_sort_recursive([20, 10])
    [10, 20]
    >>> binary_insertion_sort_recursive([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> binary_insertion_sort_recursive(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> binary_insertion_sort_recursive(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> binary_insertion_sort_recursive([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    def sort(vals):
        if not vals:
            return []
        element = vals.pop()
        output = sort(vals)
        bisect.insort_right(output, element)
        return output

    return sort(list(values))


def binary_insertion_sort_recursive_alt(values):
    """
    Alternative recursive stable binary insertion sort, creating a new list.

    See the description of binary_insertion_sort_recursive (above). This
    implementation never modifies an object after creating it, other than the
    output list it is building.

    >>> binary_insertion_sort_recursive_alt([])
    []
    >>> binary_insertion_sort_recursive_alt(())
    []
    >>> binary_insertion_sort_recursive_alt((2,))
    [2]
    >>> binary_insertion_sort_recursive_alt([10, 20])
    [10, 20]
    >>> binary_insertion_sort_recursive_alt([20, 10])
    [10, 20]
    >>> binary_insertion_sort_recursive_alt([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> binary_insertion_sort_recursive_alt(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> binary_insertion_sort_recursive_alt(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> binary_insertion_sort_recursive_alt([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    output = []

    def sort_prefix(length):
        if length == 0:
            return
        sort_prefix(length - 1)
        bisect.insort(output, values[length - 1])

    sort_prefix(len(values))
    return output


def insort_left_linear(sorted_items, new_item):
    """
    Insert an item in a sorted list at the lowest index that keeps it sorted.

    Use sequential (linear) search, so at most i + 1 comparisons are performed
    if the new item is inserted at index i. Otherwise this is like
    bisect.insort_left, except no lo, hi, or key arguments are supported.

    [Sub-exercise: Is 2-argument next (covered in semipredicate.ipynb) useful
    here? If so, use it. If not, write a comment explaining why not.]

    >>> a = [10, 20, 30, 40, 50]
    >>> insort_left_linear(a, 25)
    >>> a
    [10, 20, 25, 30, 40, 50]
    >>> b = [0, False]
    >>> insort_left_linear(b, 0.0)
    >>> b
    [0.0, 0, False]
    """
    not_too_low = (index for index, element in enumerate(sorted_items)
                   if not (new_item > element))
    insertion_point = next(not_too_low, len(sorted_items))
    sorted_items.insert(insertion_point, new_item)


def insort_right_linear(sorted_items, new_item):
    """
    Insert an item in a sorted list at the highest index that keeps it sorted.

    Use sequential (linear) search, so at most len(sorted_items) - i + 1
    comparisons are performed if the new item is inserted at index i. Otherwise
    this is like bisect.insort_right, except no lo, hi, or key arguments are
    supported.

    [Sub-exercise: Is 2-argument next (covered in semipredicate.ipynb) useful
    here? If so, use it. If not, write a comment explaining why not.]

    >>> a = [10, 20, 30, 40, 50]
    >>> insort_right_linear(a, 25)
    >>> a
    [10, 20, 25, 30, 40, 50]
    >>> b = [0, False]
    >>> insort_right_linear(b, 0.0)
    >>> b
    [0, False, 0.0]
    """
    descending_indices = range(len(sorted_items), 0, -1)
    not_too_high = (index_after for index_after, element
                    in zip(descending_indices, reversed(sorted_items))
                    if not (new_item < element))
    insertion_point = next(not_too_high, 0)
    sorted_items.insert(insertion_point, new_item)


def insertion_sort(values):
    """
    Iterative stable insertion sort, creating a new list.

    The input is not modified. The output list starts empty. It remains sorted
    after each insertion. This algorithm is adaptive: the closer to sorted its
    input already is, the less work it has to do. The insertion point is found
    by sequential search: use one of insort_left_linear or insort_right_linear.

    The worst time complexity is O(N^2). Best case scenerio inserstion is just
    an append thus O(1), thus O(N). Average time complexity over all possible
    inputs will be O(N^2) because on average we will have to move half the
    elements O(cN) = O(N).

    >>> insertion_sort([])
    []
    >>> insertion_sort(())
    []
    >>> insertion_sort((2,))
    [2]
    >>> insertion_sort([10, 20])
    [10, 20]
    >>> insertion_sort([20, 10])
    [10, 20]
    >>> insertion_sort([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> insertion_sort(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> insertion_sort(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> insertion_sort([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    output = []
    for element in values:
        insort_right_linear(output, element)
    return output


def insertion_sort_recursive(values):
    """
    Recursive stable insertion sort, creating a new list.

    See the description of insertion_sort above. (There is little reason to
    implement this recursively in Python, except as an exercise, and for
    conceptual clarity.) This should use whichever of insort_left_linear or
    insort_right_linear insertion_sort uses. Ensure the best, average, and
    worst-case asymptotic time complexities are the same as in insertion_sort;
    avoid incurring asymptotically worse performance from copying. Assume
    values is a sequence.

    >>> insertion_sort_recursive([])
    []
    >>> insertion_sort_recursive(())
    []
    >>> insertion_sort_recursive((2,))
    [2]
    >>> insertion_sort_recursive([10, 20])
    [10, 20]
    >>> insertion_sort_recursive([20, 10])
    [10, 20]
    >>> insertion_sort_recursive([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> insertion_sort_recursive(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> insertion_sort_recursive(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> insertion_sort_recursive([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    def sort(vals):
        if not vals:
            return []
        element = vals.pop()
        output = sort(vals)
        insort_right_linear(output, element)
        return output

    return sort(list(values))


def insertion_sort_recursive_alt(values):
    """
    Alternative recursive stable insertion sort, creating a new list.

    See the description of insertion_sort_recursive (above). This
    implementation never modifies an object after creating it, other than
    through the call to insort_left_linear or insort_right_linear, which
    modifies the output list being built.

    >>> insertion_sort_recursive_alt([])
    []
    >>> insertion_sort_recursive_alt(())
    []
    >>> insertion_sort_recursive_alt((2,))
    [2]
    >>> insertion_sort_recursive_alt([10, 20])
    [10, 20]
    >>> insertion_sort_recursive_alt([20, 10])
    [10, 20]
    >>> insertion_sort_recursive_alt([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> insertion_sort_recursive_alt(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> insertion_sort_recursive_alt(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> insertion_sort_recursive_alt([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    output = []

    def sort_prefix(length):
        if length == 0:
            return
        sort_prefix(length - 1)
        insort_right_linear(output, values[length - 1])

    sort_prefix(len(values))
    return output


def insertion_sort_in_place(values):
    """
    Stable in-place insertion sort. Permutes values. O(1) auxiliary space.

    This should have the same best, average, and worst-case time complexity as
    insertion_sort. Nether use nor rewrite any functionality from "insort"
    functions in this or the bisect module. You can use any approach to
    iteration here, even if it seems un-Pythonic.

    Please read the description in insertion_sort_in_place_alt before starting.

    >>> def test(a): print(insertion_sort_in_place(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> test([0.0, 0, False])  # It's a stable sort.
    None; [0.0, 0, False]
    """
    for right in range(1, len(values)):
        elem = values[right]
        left = right
        while left > 0 and elem < values[left - 1]:
            values[left] = values[left - 1]
            left -= 1
        values[left] = elem


def insertion_sort_in_place_alt(values):
    """
    Stable in-place insertion sort. Permutes values. O(1) auxiliary space.

    This is an alternate implementation of insertion_sort_in_place with all the
    same asymptotic time and space complexities. That exercise's allowed and
    disallowed techniques apply here, too.

    One of the implementations mutates values only by assignments of the form
    values[x] = y (with some expressions in place of x and y). The other
    mutates values only by swapping its elements. Neither uses slicing.

    >>> def test(a): print(insertion_sort_in_place_alt(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> test([0.0, 0, False])  # It's a stable sort.
    None; [0.0, 0, False]
    """
    for right in range(1, len(values)):
        for left in range(right, 0, -1):
            if not values[left] < values[left - 1]:
                break
            values[left], values[left - 1] = values[left - 1], values[left]


def _priority_queue_sort(values, max_pq_factory):
    """Make a low-to-high sorted copy of values, using a max priority queue."""
    pq = max_pq_factory()
    for val in values:
        pq.enqueue(val)

    out = [pq.dequeue() for _ in range(len(pq))]
    out.reverse()
    return out


# FIXME: Change "alt" in this function name to a more descriptive short suffix.
def insertion_sort_alt(values):
    """
    Stable (sequential or binary) insertion sort, creating a new list.

    This alternate implementation of binary_insertion_sort or insertion_sort
    makes good use of a data structure already implemented in another module of
    this project. This has the same best, average, and worst-case time
    complexities as insertion_sort, but all but O(n) work will be done inside
    the methods of that data structure.

    >>> insertion_sort_alt([])
    []
    >>> insertion_sort_alt(())
    []
    >>> insertion_sort_alt((2,))
    [2]
    >>> insertion_sort_alt([10, 20])
    [10, 20]
    >>> insertion_sort_alt([20, 10])
    [10, 20]
    >>> insertion_sort_alt([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> insertion_sort_alt(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> insertion_sort_alt(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> insertion_sort_alt([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    return _priority_queue_sort(values, queues.FastDequeueMaxPriorityQueue)


def selection_sort(values):
    """
    Sort by repeatedly finding minimum or maximum values, creating a new list.

    Most selection sort implementations, including this one, are unstable. That
    lets them be significantly simpler and also faster by a constant factor.

    [FIXME: State best, average, and worst case asymptotic time complexities.]

    >>> selection_sort([])
    []
    >>> selection_sort(())
    []
    >>> selection_sort((2,))
    [2]
    >>> selection_sort([10, 20])
    [10, 20]
    >>> selection_sort([20, 10])
    [10, 20]
    >>> selection_sort([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> selection_sort(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> selection_sort(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    """
    dup = list(values)
    out = []

    while dup:
        index, _ = min(enumerate(dup), key=operator.itemgetter(1))
        dup[index], dup[-1] = dup[-1], dup[index]
        out.append(dup.pop())

    return out


def selection_sort_stable(values):
    """
    Stable selection sort. Like selection_sort above, but stable.

    [FIXME: Make sure you understand both of the main ways to implement this,
    and also are aware of at least one data structure where selection sort is
    naturally stable, and why that is. Replace this paragraph with a brief
    description of whatever aspects of those issues you regard helpful for this
    docstring. (If that is none of it, then just delete this paragraph.)]

    >>> selection_sort_stable([])
    []
    >>> selection_sort_stable(())
    []
    >>> selection_sort_stable((2,))
    [2]
    >>> selection_sort_stable([10, 20])
    [10, 20]
    >>> selection_sort_stable([20, 10])
    [10, 20]
    >>> selection_sort_stable([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> selection_sort_stable(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> selection_sort_stable(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> selection_sort_stable([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    >>> selection_sort_stable([None])  # You don't need to special-case this.
    [None]
    """
    blank = object()
    dup = list(values)
    out = []

    for _ in range(len(dup)):
        with_indices = ((i, x) for i, x in enumerate(dup) if x is not blank)
        index, value = min(with_indices, key=operator.itemgetter(1))
        dup[index] = blank
        out.append(value)

    return out


def selection_sort_in_place(values):
    """
    Unstable in-place selection sort. Permutes values. O(1) auxiliary space.

    >>> def test(a): print(selection_sort_in_place(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    """
    for left in range(0, len(values) - 1):
        best_right = min(range(left, len(values)), key=values.__getitem__)
        values[left], values[best_right] = values[best_right], values[left]


# FIXME: Change "alt" in this function name to a more descriptive short suffix.
# FIXME: Extract any major shared logic to a module-level nonpublic function.
def selection_sort_alt(values):
    """
    Sort by repeatedly finding minimum or maximum values, creating a new list.

    This alternate implementation of selection_sort makes good use of a data
    structure already implemented in another module of this project. This has
    the same best, average, and worst-case time complexities as selection_sort,
    but all but O(n) work will be done inside methods of that data structure.)

    >>> selection_sort_alt([])
    []
    >>> selection_sort_alt(())
    []
    >>> selection_sort_alt((2,))
    [2]
    >>> selection_sort_alt([10, 20])
    [10, 20]
    >>> selection_sort_alt([20, 10])
    [10, 20]
    >>> selection_sort_alt([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> selection_sort_alt(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> selection_sort_alt(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    """
    return _priority_queue_sort(values, queues.FastEnqueueMaxPriorityQueue)


def least_k(values, k):
    """
    Return a new sorted list of the k smallest elements of values. Unstable.

    The algorithm used here takes O(n * k) time, even though an O(n + k log n)
    algorithm exists. But evaluating sorted(values)[:k], where the sorted call
    takes O(n log n) time, is sometimes too slow even for O(n * k). This
    function is accordingly most reasonable to use when k is very small.

    This need not be stable: it returns a length-k prefix of some sorted
    permutation of values, but not necessarily of sorted(values). If x is in
    the returned list of k elements of values, and y is an unreturned element,
    all you must guarantee is that y is not less than x.

    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> b = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> [least_k(a, k) == b[:k] for k in range(len(a) + 1)]
    [True, True, True, True, True, True, True, True, True, True, True]
    >>> a
    [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    """
    dup = list(values)

    for left in range(0, k):
        best_right = min(range(left, len(dup)), key=dup.__getitem__)
        dup[left], dup[best_right] = dup[best_right], dup[left]

    return dup[:k]


def greatest_k(values, k):
    """
    Return a new sorted list of the k largest elements of values. Unstable.

    The algorithm used here takes O(n * k) time, even though an O(n + k log n)
    algorithm exists. But evaluating sorted(values)[-k:] (for k > 0), where the
    sorted call takes O(n log n) time, is sometimes too slow even for O(n * k).
    This function is accordingly most reasonable to use when k is very small.

    This need not be stable: it returns a length-k suffix of some sorted
    permutation of values, but not necessarily of sorted(values). If x is in
    the returned list of k elements of values, and y is an unreturned element,
    all you must guarantee is that y is not greater than x.

    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> b = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> [greatest_k(a, k) == b[len(a) - k:] for k in range(11)]
    [True, True, True, True, True, True, True, True, True, True, True]
    >>> a
    [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    """
    dup = list(values)

    for right in range(len(values) - 1, len(values) - 1 - k, -1):
        best_left = max(range(right + 1), key=dup.__getitem__)
        dup[right], dup[best_left] = dup[best_left], dup[right]

    return dup[len(dup) - k:]  # Because dup[:k] needs k=0 to be special-cased.


def select_k(values, k):
    """
    Find a kth order statistic (0-based indexing) in O(n * min(k, n - k)) time.

    This need not be stable: it returns an object appearing at index k in some
    sorted permutation of values, but not necessarily sorted(values). Using
    sorted(values)[k] would often be faster than this, but k can be close
    enough to 0, or close enough to n, to make the O(n log n) sort is too slow.

    This can be solved faster than O(n * min(k, n - k)), but this exercise
    isn't about that. Relatedly, call other functions in this module instead of
    duplicating their functionality.

    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> [select_k(a, i) for i in range(len(a))]
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> a
    [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    """
    left_distance = k + 1
    right_distance = len(values) - k

    if right_distance < left_distance:
        return greatest_k(values, right_distance)[0]

    return least_k(values, left_distance)[-1]


def my_shuffle(values):
    """
    Randomly shuffle a sequence, in place, in linear time. Like random.shuffle.

    Feel free to use random-number generation functions that return integers
    from an interval. Do not use any other standard library facilities related
    to randomness. All permutations of the objects should be equally likely,
    but this need not be so unpredictable as to be safe for cryptographic use.
    That is, like random.shuffle, this function must not be used for tasks like
    generating encryption keys, passwords, or password-database salts.

    See test_shuffle in permutations.ipynb to manually test this function.
    """
    for left in range(len(values) - 1):
        right = random.randrange(left, len(values))
        values[left], values[right] = values[right], values[left]


def merge_two_slow(values1, values2):
    """
    Return a sorted list of items from two sorted sequences, in quadratic time.

    Separate items that appear in the same list always appear in the output in
    that order. In addition, this is a stable merge: whenever it won't prevent
    the output from being sorted, items in values1 appear in the output before
    those in values2 (i.e., ties are broken in favor of items in values1).

    If values1 is empty, this is equivalent to a binary insertion sort, which
    is to say that the input sequences' sortedness is not being taken advantage
    of here. This algorithm takes quadratic time in the worst and average case.

    >>> merge_two_slow([1, 3, 5], [2, 4, 6])
    [1, 2, 3, 4, 5, 6]
    >>> merge_two_slow([2, 4, 6], [1, 3, 5])
    [1, 2, 3, 4, 5, 6]
    >>> merge_two_slow([], [2, 4, 6])
    [2, 4, 6]
    >>> merge_two_slow((), [2, 4, 6])
    [2, 4, 6]
    >>> merge_two_slow((), [])
    []
    >>> merge_two_slow([], ())
    []
    >>> merge_two_slow((), (1, 1, 4, 7, 8))
    [1, 1, 4, 7, 8]
    >>> merge_two_slow((1, 1, 4, 7, 8), ())
    [1, 1, 4, 7, 8]
    """
    resultlist = list(values1)
    for v2 in values2:
        bisect.insort_right(resultlist, v2)

    return resultlist


def merge_two(values1, values2):
    """
    Return a sorted list of items from two sorted sequences, in linear time.

    Separate items that appear in the same list always appear in the output in
    that order. In addition, this is a stable merge: whenever it won't prevent
    the output from being sorted, items in values1 appear in the output before
    those in values2 (i.e., ties are broken in favor of items in values1).

    This takes full advantage of values1 and values2 already separately being
    sorted. It always takes O(len(values1) + len(values2)) time, i.e., linear.

    >>> merge_two([1, 3, 5], [2, 4, 6])
    [1, 2, 3, 4, 5, 6]
    >>> merge_two([2, 4, 6], [1, 3, 5])
    [1, 2, 3, 4, 5, 6]
    >>> merge_two([], [2, 4, 6])
    [2, 4, 6]
    >>> merge_two((), [2, 4, 6])
    [2, 4, 6]
    >>> merge_two((), [])
    []
    >>> merge_two([], ())
    []
    >>> merge_two((), (1, 1, 4, 7, 8))
    [1, 1, 4, 7, 8]
    >>> merge_two((1, 1, 4, 7, 8), ())
    [1, 1, 4, 7, 8]
    """
    resultlist = []
    index = 0

    for v1 in values1:
        # Take everything from values2 that must be output before v1.
        while index < len(values2) and values2[index] < v1:
            resultlist.append(values2[index])
            index += 1

        resultlist.append(v1)

    resultlist.extend(values2[index:])

    return resultlist


def merge_two_alt(values1, values2):
    """
    Return a sorted list of items from two sorted sequences, in linear time.

    Separate items that appear in the same list always appear in the output in
    that order. In addition, this is a stable merge: whenever it won't prevent
    the output from being sorted, items in values1 appear in the output before
    those in values2 (i.e., ties are broken in favor of items in values1).

    This is another way to implement the algorithm in merge_two. So it also
    takes linear time in all cases.

    >>> merge_two_alt([1, 3, 5], [2, 4, 6])
    [1, 2, 3, 4, 5, 6]
    >>> merge_two_alt([2, 4, 6], [1, 3, 5])
    [1, 2, 3, 4, 5, 6]
    >>> merge_two_alt([], [2, 4, 6])
    [2, 4, 6]
    >>> merge_two_alt((), [2, 4, 6])
    [2, 4, 6]
    >>> merge_two_alt((), [])
    []
    >>> merge_two_alt([], ())
    []
    >>> merge_two_alt((), (1, 1, 4, 7, 8))
    [1, 1, 4, 7, 8]
    >>> merge_two_alt((1, 1, 4, 7, 8), ())
    [1, 1, 4, 7, 8]
    """
    resultlist = []
    index1 = 0
    index2 = 0

    while index1 < len(values1) and index2 < len(values2):
        if values2[index2] < values1[index1]:
            resultlist.append(values2[index2])
            index2 += 1
        else:
            resultlist.append(values1[index1])
            index1 += 1

    resultlist.extend(values1[index1:] or values2[index2:])

    return resultlist


def merge_sort(values, *, merge=merge_two):
    """
    Merge sort recursively using a two way merge function.

    >>> merge_sort([])
    []
    >>> merge_sort(())
    []
    >>> merge_sort((2,))
    [2]
    >>> merge_sort([10, 20])
    [10, 20]
    >>> merge_sort([20, 10])
    [10, 20]
    >>> merge_sort([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> merge_sort(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> merge_sort(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> merge_sort([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    def helper(values):
        # base case: length is less than 2, return the list
        if len(values) < 2:
            return values

        halfway = len(values) // 2
        return merge(helper(values[:halfway]), helper(values[halfway:]))

    return helper(list(values))


def merge_sort_bottom_up_unstable(values, *, merge=merge_two):
    """
    Mergesort bottom-up, using a two way merge function, iteratively. Unstable.

    This implementation is an unstable sort. Both top-down and bottom-up
    mergesorts are typically stable, and stable implementations tend to be
    strongly preferred, but one of the notable approaches to bottom-up
    mergesort is unstable. This is the same algorithm as presented in
    *Algorithms* by Dasgupta, Papadimitriou, and Vazirani, 1st ed., p.51.

    >>> merge_sort_bottom_up_unstable([])
    []
    >>> merge_sort_bottom_up_unstable(())
    []
    >>> merge_sort_bottom_up_unstable((2,))
    [2]
    >>> merge_sort_bottom_up_unstable([10, 20])
    [10, 20]
    >>> merge_sort_bottom_up_unstable([20, 10])
    [10, 20]
    >>> merge_sort_bottom_up_unstable([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> merge_sort_bottom_up_unstable(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> merge_sort_bottom_up_unstable(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> merge_sort_bottom_up_unstable([7, 6, 5, 4, 3, 2, 1])
    [1, 2, 3, 4, 5, 6, 7]
    >>> merge_sort_bottom_up_unstable([0.0, 0, False])  # doctest: +SKIP
    [0.0, 0, False]
    """
    if not values:
        return []

    queue = collections.deque([x] for x in values)

    while len(queue) > 1:
        left = queue.popleft()
        right = queue.popleft()
        queue.append(merge(left, right))

    return queue[0]


def merge_sort_bottom_up(values, *, merge=merge_two):
    """
    Sort bottom-up, using a two way merge function, iteratively. Stable.

    >>> merge_sort_bottom_up([])
    []
    >>> merge_sort_bottom_up(())
    []
    >>> merge_sort_bottom_up((2,))
    [2]
    >>> merge_sort_bottom_up([10, 20])
    [10, 20]
    >>> merge_sort_bottom_up([20, 10])
    [10, 20]
    >>> merge_sort_bottom_up([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> merge_sort_bottom_up(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> merge_sort_bottom_up(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> merge_sort_bottom_up([7, 6, 5, 4, 3, 2, 1])
    [1, 2, 3, 4, 5, 6, 7]
    >>> merge_sort_bottom_up([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    if not values:
        return []

    queue = collections.deque([x] for x in values)
    queue2 = collections.deque()

    while len(queue) > 1:
        queue, queue2 = queue2, queue

        while len(queue2) > 1:
            left = queue2.popleft()
            right = queue2.popleft()
            queue.append(merge(left, right))

        if queue2:
            queue.append(queue2.popleft())

    return queue[0]


# !!FIXME: When removing implementation bodies, erase "*, merge=merge_two" too.
def merge_many(sorted_lists, *, merge=merge_two):
    """
    Recursively stably merge any number of sorted lists into a new sorted list.

    With n total elements across k lists, the worst-case time is O(n log k).

    >>> merge_many([])
    []
    >>> merge_many(())
    []
    >>> merge_many([[3]])
    [3]
    >>> merge_many([x] for x in range(10, 0, -1))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> ''.join(merge_many(collections.deque([
    ...     ['b', 'b'], ['a', 'c', 'd'], ['b', 'f'], ['a', 'b', 'c', 'd', 'e'],
    ...     [], ['c', 'f'], ['c', 'g'], ['f', 'h'], ['a', 'e'], ['b', 'h'], [],
    ...     ['b'], ['c', 'x'], ['a', 'b', 'c'], ['w' ,'y'], ['w', 'z'], ['v'],
    ... ])))  # Test with a deque, since it is a weird non-sliceable sequence.
    'aaaabbbbbbbccccccddeefffghhvwwxyz'
    >>> merge_many([[0.0, 1.0, 2.0, 3.0], [-1, 0, 1, 2, 3, 4], [False, True]])
    [-1, 0.0, 0, False, 1.0, 1, True, 2.0, 2, 3.0, 3, 4]
    """
    def helper(branches):
        match branches:
            case []:
                return []
            case [seq]:
                return list(seq)
            case _:
                half = len(branches) // 2
                return merge(helper(branches[:half]), helper(branches[half:]))

    return helper(list(sorted_lists))


# !!FIXME: When removing implementation bodies, erase "*, merge=merge_two" too.
def merge_many_bottom_up(sorted_lists, *, merge=merge_two):
    """
    Iteratively stably merge any number of sorted lists into a new sorted list.

    This is like merge_many, but that is top-down and recursive, while this is
    bottom-up and uses no recursion. Asymptotic time complexities are the same.

    >>> merge_many_bottom_up([])
    []
    >>> merge_many_bottom_up(())
    []
    >>> merge_many_bottom_up([[3]])
    [3]
    >>> merge_many_bottom_up([x] for x in range(10, 0, -1))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> ''.join(merge_many_bottom_up(collections.deque([
    ...     ['b', 'b'], ['a', 'c', 'd'], ['b', 'f'], ['a', 'b', 'c', 'd', 'e'],
    ...     [], ['c', 'f'], ['c', 'g'], ['f', 'h'], ['a', 'e'], ['b', 'h'], [],
    ...     ['b'], ['c', 'x'], ['a', 'b', 'c'], ['w' ,'y'], ['w', 'z'], ['v'],
    ... ])))  # Test with a deque, since it is a weird non-sliceable sequence.
    'aaaabbbbbbbccccccddeefffghhvwwxyz'
    >>> merge_many_bottom_up([
    ...     [0.0, 1.0, 2.0, 3.0], [-1, 0, 1, 2, 3, 4], [False, True]
    ... ])
    [-1, 0.0, 0, False, 1.0, 1, True, 2.0, 2, 3.0, 3, 4]
    """
    if not sorted_lists:
        return []

    current = collections.deque(sorted_lists)
    previous = collections.deque()

    while len(current) > 1:
        current, previous = previous, current

        while len(previous) > 1:
            left = previous.popleft()
            right = previous.popleft()
            current.append(merge(left, right))

        if previous:
            current.append(previous.popleft())

    return current[0]


def _monotone_runs(values):  # !!FIXME: Simplify this implementation.
    """
    Split values into preserved nondecreasing and reversed decreasing runs.

    This divides input values into non-interleaved rising (non-decreasing) and
    falling (strictly decreasing) runs, reverses falling runs, and concatenates
    reversed falling runs with adjacent rising runs when correct to do so.

    >>> _monotone_runs([])
    []
    >>> _monotone_runs([42])
    [[42]]
    >>> _monotone_runs([13, 12, 9, 7, 3, 1, 5, 2, 4, 6, 8, 10, 11])
    [[1, 3, 7, 9, 12, 13], [2, 5], [4, 6, 8, 10, 11]]
    >>> _monotone_runs([3, 6, 2, 1, 3, 6, 0, 5, 5, 0, 1, 4, 2, 4])
    [[3, 6], [1, 2, 3, 6], [0, 5, 5], [0, 1, 4], [2, 4]]
    >>> _monotone_runs(['C', 'B', 'A', 'P', 'Q'])
    [['A', 'B', 'C', 'P', 'Q']]
    >>> _monotone_runs(['C', 'B', 'A', 'Q', 'P'])
    [['A', 'B', 'C', 'Q'], ['P']]
    >>> from fractions import Fraction as F
    >>> _monotone_runs([F(0, 1), True, 1, False, F(1, 1), 0, 1.0, 0.0])
    [[Fraction(0, 1), True, 1], [False, Fraction(1, 1)], [0, 1.0], [0.0]]
    >>> _monotone_runs([2, F(0, 1), True, 1, False, F(1, 1), 0, 1.0, 0.0])
    [[Fraction(0, 1), 2], [True, 1], [False, Fraction(1, 1)], [0, 1.0], [0.0]]
    """
    runs = []  # Rising (really, nondescending) runs.
    falling = []  # A falling (strictly descending) run.

    def process_falling():
        nonlocal falling

        if runs and not falling[-1] < runs[-1][-1]:
            # Extend the previous rising run.
            runs[-1].extend(reversed(falling))
            falling.clear()
        else:
            # Add a new rising run.
            falling.reverse()
            runs.append(falling)
            falling = []

    for val in values:
        if falling:
            if val < falling[-1]:
                # Continue the current falling run.
                falling.append(val)
                continue

            process_falling()

        if runs and not val < runs[-1][-1]:
            # Continue the current rising run.
            runs[-1].append(val)
        else:
            # Start a falling run.
            falling.append(val)

    if falling:
        process_falling()

    return runs


def merge_sort_adaptive(values, *, merge=merge_two):
    """
    Highly adaptive implementation of stable recursive top-down mergesort.

    Real-world input for sorting algorithms is often non-random. In particular,
    it is common that real data have much longer monotone runs than random
    data. "Monotone" means "not changing direction." Data are sometimes almost
    sorted or almost reverse-sorted, or have sorted and reverse-sorted pieces.

    Take advantage of this to design and implement an algorithm with worst and
    average case O(n log n) time but best-case O(n) time, so the best case,
    though rare among all possible inputs, is fairly common in practice. On
    data that seldom change direction, this will usually finish in near-linear
    time. Most real-world data will benefit some, even if not achieving O(n).

    See recursion-hints.ipynb for hints (if needed).

    [FIXME: State the running time in terms of both n and the number of
    direction changes in the input, or some related variable.]

    >>> merge_sort_adaptive([])
    []
    >>> merge_sort_adaptive(())
    []
    >>> merge_sort_adaptive((2,))
    [2]
    >>> merge_sort_adaptive([10, 20])
    [10, 20]
    >>> merge_sort_adaptive([20, 10])
    [10, 20]
    >>> merge_sort_adaptive([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> merge_sort_adaptive(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> merge_sort_adaptive(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> merge_sort_adaptive([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    return merge_many(_monotone_runs(values), merge=merge)


def merge_sort_adaptive_bottom_up(values, *, merge=merge_two):
    """
    Highly adaptive implementation of stable iterative bottom-up mergesort.

    This is like merge_sort_adaptive, but that is top-down and recursive, while
    this is bottom-up and uses no recursion. Their asymptotic time complexities
    are the same, both in terms of n alone, and in terms of n and the number of
    direction changes or some related variable.

    FIXME: If the two implementations share substantial logic, factor that out
    into a module-level nonpublic function. You might also find it helpful to
    write tests for that function, to be confident these implementations work
    the way you intend and are as fully adaptive as you intend.

    >>> merge_sort_adaptive_bottom_up([])
    []
    >>> merge_sort_adaptive_bottom_up(())
    []
    >>> merge_sort_adaptive_bottom_up((2,))
    [2]
    >>> merge_sort_adaptive_bottom_up([10, 20])
    [10, 20]
    >>> merge_sort_adaptive_bottom_up([20, 10])
    [10, 20]
    >>> merge_sort_adaptive_bottom_up([3, 3])
    [3, 3]
    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> merge_sort_adaptive_bottom_up(a)
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> b = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
    >>> merge_sort_adaptive_bottom_up(b)
    ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> merge_sort_adaptive_bottom_up([0.0, 0, False])  # It's a stable sort.
    [0.0, 0, False]
    """
    return merge_many_bottom_up(_monotone_runs(values), merge=merge)


# FIXME: In the four mutating mergesorts below, extract logic to non-public
# module-level functions when doing so reduces duplication of logic, improves
# clarity, or achieves useful modularity. In this case, it is possible that you
# will choose to keep some of the logic duplicated, for conceptual clarity or
# readability. But most duplication should be avoided. If you choose to keep
# some code duplicated here, you should consider duplicating it across separate
# top-level helpers so as to still achieve modularity. Note that your initial
# implementations of the four mutating mergesorts may or may not follow any of
# this advice, but if not, then you should refactor them once they are working.
# Each of the four public mergesorts will likely end up with a one-line body.


def _merge_mut_simple(values, low, mid, high, aux):
    """
    Merge values[low:mid] and values[mid:high] in values.

    This implementation is not adaptive.
    """
    assert not aux, 'The auxiliary storage list must start empty.'

    left = low
    right = mid

    while left < mid and right < high:
        if values[right] < values[left]:
            aux.append(values[right])
            right += 1
        else:
            aux.append(values[left])
            left += 1

    # This un-Pythonic copying ensures all but O(1) auxiliary space is in aux.
    # That's an artificial exercise requirement. Usually don't do it this way.
    while left < mid:
        aux.append(values[left])
        left += 1
    while right < high:
        aux.append(values[right])
        right += 1

    values[low:high] = aux
    aux.clear()


def _merge_mut(values, low, mid, high, aux):
    """
    Merge values[low:mid] and values[mid:high] in values.

    This implementation is adaptive, though not aggressively so.
    """
    if not values[mid] < values[mid - 1]:
        return  # Already merged by trivial concatenation.

    assert not aux, 'The auxiliary storage list must start empty.'

    left = low
    right = mid

    while left < mid and right < high:
        if values[right] < values[left]:
            aux.append(values[right])
            right += 1
        else:
            aux.append(values[left])
            left += 1

    # This un-Pythonic copying ensures all but O(1) auxiliary space is in aux.
    # That's an artificial exercise requirement. Usually don't do it this way.
    while left < mid:
        aux.append(values[left])
        left += 1

    assert len(aux) == right - low, 'Miscount of copied elements in merge.'
    values[low:right] = aux
    aux.clear()


def _do_merge_sort_mut(values, low, high, aux, merge):
    """
    Top-down mergesort values[low:high] in values with the given 2-way merger.
    """
    if high - low < 2:
        return

    mid = (low + high) // 2
    _do_merge_sort_mut(values, low, mid, aux, merge)
    _do_merge_sort_mut(values, mid, high, aux, merge)
    merge(values, low, mid, high, aux)


def merge_sort_mut_simple(values):
    """
    Recursively stably mergesort values top-down, rearranging it. Nonadaptive.

    This uses a helper function whose parameters include low, mid, and high,
    that merges values[low:mid] and values[mid:high] into values[low:high]. It
    may or may not have other parameters. It need not be the only helper used.

    That opens the door for some straightforward adaptivity optimizations, but
    this function is not adaptive. See merge_sort_mut below.

    [FIXME: State the best, average, and worst-case time complexity.]

    O(n) auxiliary space is permitted. However, all but O(log n) auxiliary
    space used as a result of a call to merge_sort_mut_simple must be in the
    same list object, including space used in separate calls to the helper.
    (Such a list need not be pre-sized. Its length may fluctuate as you like.)

    That restriction may make this function faster or slower than otherwise,
    depending on the Python and standard library implementations. The reason
    this exercise insists on doing it that way is that it is closer to how you
    would usually implement mergesort in some other important languages like C.

    >>> def test(a): print(merge_sort_mut_simple(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> test([0.0, 0, False])  # It's a stable sort.
    None; [0.0, 0, False]
    """
    _do_merge_sort_mut(values, 0, len(values), [], _merge_mut_simple)


def merge_sort_mut(values):
    """
    Recursively stably mergesort values top-down, rearranging it. Adaptive.

    This uses a helper function whose parameters include low, mid, and high,
    that merges values[low:mid] and values[mid:high] into values[low:high]. It
    may or may not have other parameters. It need not be the only helper used.

    That opens the door for two straightforward forms of adaptivity. Ensure:

    (1) A merge that doesn't change the order of elements takes O(1) time.

    (2) When merging mid - low == m elements with high - mid == n elements, if
        the order of the rightmost k < n elements is unchanged, the merge takes
        O(m + n - k) time. [If k == n, optimization (1) is performed instead.]

    Taken together, this is still far less aggressively adaptive than the mixed
    run-detecting implementation in merge_sort_adaptive, but it can still help.

    [FIXME: State the best, average, and worst-case time complexity.]

    O(n) auxiliary space is permitted, but all but O(log n) of it must use the
    same list object. See merge_sort_mut_simple for more on this requirement.

    >>> def test(a): print(merge_sort_mut(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> test([0.0, 0, False])  # It's a stable sort.
    None; [0.0, 0, False]
    """
    _do_merge_sort_mut(values, 0, len(values), [], _merge_mut)


def _do_merge_sort_mut_bottom_up(values, merge):
    """
    Bottom-up mergesort values, rearranging it, with the given 2-way merger.
    """
    aux = []

    delta = 1
    while delta < len(values):
        for low in range(0, len(values) - delta, delta * 2):
            mid = low + delta
            high = min(mid + delta, len(values))
            merge(values, low, mid, high, aux)
        delta *= 2


def merge_sort_mut_bottom_up_simple(values):
    """
    Iteratively stably mergesort values bottom-up, rearranging it. Nonadaptive.

    This uses a helper function whose parameters include low, mid, and high,
    that merges values[low:mid] and values[mid:high] into values[low:high]. It
    may or may not have other parameters. It need not be the only helper used.

    That opens the door for some straightforward adaptivity optimizations, but
    this function is not adaptive. See merge_sort_mut_bottom_up below.

    [FIXME: State the best, average, and worst-case time complexity.]

    O(n) auxiliary space is permitted, but all but O(1) of it must use the same
    list object. See merge_sort_mut_simple for more on this requirement. Note
    that O(log n) was allowed outside the list there. Only O(1) is needed
    outside it here, because [FIXME: state the reason].

    >>> def test(a): print(merge_sort_mut_bottom_up_simple(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> test([0.0, 0, False])  # It's a stable sort.
    None; [0.0, 0, False]
    """
    _do_merge_sort_mut_bottom_up(values, _merge_mut_simple)


def merge_sort_mut_bottom_up(values):
    """
    Iteratively stably mergesort values bottom-up, rearranging it. Adaptive.

    This uses a helper function whose parameters include low, mid, and high,
    that merges values[low:mid] and values[mid:high] into values[low:high]. It
    may or may not have other parameters. It need not be the only helper used.

    This is somewhat adaptive. As in merge_sort_mut, ensure:

    (1) A merge that doesn't change the order of elements takes O(1) time.

    (2) When merging mid - low == m elements with high - mid == n elements, if
        the order of the rightmost k < n elements is unchanged, the merge takes
        O(m + n - k) time. [If k == n, optimization (1) is performed instead.]

    [FIXME: State the best, average, and worst-case time complexity.]

    O(n) auxiliary space is permitted, but all but O(1) of it must use the same
    list object. See merge_sort_mut_simple and merge_sort_mut_bottom_up_simple.

    >>> def test(a): print(merge_sort_mut_bottom_up(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    >>> test([0.0, 0, False])  # It's a stable sort.
    None; [0.0, 0, False]
    >>> merge_sort_mut_bottom_up(range(1000))  # Works without special casing.
    """
    _do_merge_sort_mut_bottom_up(values, _merge_mut)


# !!FIXME: When removing implementation bodies, remove this too.
Parts = collections.namedtuple('Parts', ('lt', 'eq', 'gt'))

Parts.__doc__ = """
Result of calling partition_three.

Items less than, equal (or similar) to, and greater than some pivot.
"""


def partition_three(values, pivot):
    """
    Stable 3-way partition.

    Returns lists of values less than, similar to, and greater than the pivot,
    as a named tuple (where x is similar to y when neither x < y nor y < x).

    The asymptotic time complexity is the best possible for this problem.
    [FIXME: Note it here.]

    NOTE: Another kind of 3-way partitioning is strictly more powerful than
    this, and more commonly used: dual-pivot partitioning. It uses two pivot
    values, so each element orders before both pivots, between them, or after
    both. Take "≾" to mean "not greater than" (for weak ordering). With pivots
    p1 ≾ p2, each x may be grouped by whether x ≾ p1, p1 < x ≾ p2, or p2 < x;
    or by whether x < p1, p1 ≾ x < p2, or p2 ≾ x; or by some other breakdown.
    Grouping by whether x < p1, p1 ≾ x ≾ p2, or p2 < x is uncommon but has the
    advantage that it can be used to do single-pivot 3-way partitioning by
    [FIXME: briefly state the simple way this can be achieved].

    This function, and partition_three_in_place (below), do single-pivot 3-way
    partitioning. Accompanying exercises develop partition-based selection and
    sorting algorithms that use them. Those selection and sorting algorithms
    can be modified to use, and benefit from, dual-pivot 3-way partitioning,
    which is usually preferable. Although single-pivot 3-way partitioning is
    sometimes useful in practice, these exercises use it for simplicity, much
    as they omit key= and reverse= support. But future exercises may involve
    those and other refinements (perhaps in a new module, sorting.py).

    >>> partition_three([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0], 4)
    Parts(lt=[3, -17, 1, 2, -15, 1, -1, 0], eq=[4], gt=[5, 8, 66, 9, 5, 8])
    >>> partition_three([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0], 5)
    Parts(lt=[3, -17, 1, 4, 2, -15, 1, -1, 0], eq=[5, 5], gt=[8, 66, 9, 8])
    >>> isinstance(_, tuple)
    True
    """
    lower = []
    similar = []
    higher = []

    for value in values:
        if value < pivot:
            lower.append(value)
        elif pivot < value:
            higher.append(value)
        else:
            similar.append(value)

    return Parts(lower, similar, higher)


# !!FIXME: Reword. The range of insertion points includes the right endpoint.
def similar_range(values, new_value):
    """
    Find the range of valid insertion points for new_value in sorted(values).

    (When new_value is already present in values, this is the same as the range
    of indices where new_value could appear in an arbitrary sorted permutation
    of values, i.e., in a sorting of values without any stability guarantee.)

    The asymptotic time complexity is the best possible for this problem:
    [FIXME: Note it here.]

    See also similar_range_alt below.

    >>> a = [5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0]
    >>> similar_range(a, 4)
    range(8, 9)
    >>> similar_range(a, 5)
    range(9, 11)
    """
    lower, similar, _ = partition_three(values, new_value)
    return range(len(lower), len(lower) + len(similar))


# !!FIXME: Reword. The range of insertion points includes the right endpoint.
def similar_range_alt(values, new_value):
    """
    Find the range of valid insertion points for new_value in sorted(values).

    This is an alternate implementation of similar_range. One uses
    partition_three for all but O(1) of its work. The other uses O(1) auxiliary
    space. Both are single-pass. They have the same asymptotic time complexity.

    >>> a = [5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0]
    >>> similar_range_alt(a, 4)
    range(8, 9)
    >>> similar_range_alt(a, 5)
    range(9, 11)
    """
    lower = similar = 0

    for value in values:
        if value < new_value:
            lower += 1
        elif not new_value < value:
            similar += 1

    return range(lower, lower + similar)


# TODO: Rename this after the "select by partitioning" algorithm it implements.
def select_by_partitioning(values, k):
    """
    Recursively find the stable kth order statistic or raise IndexError.

    This finds the item at nonnegative (0-based) index k in a stable sort. Thus

        select_by_partitioning(values, k) is sorted(values)[k]

    evaluates to True when possible, and otherwise raises IndexError.

    You can assume isinstance(k, int). If k is negative, raise IndexError.

    The technique used is partition-based, calling partition_three. Average
    time complexity is asymptotically optimal, but worst-case time complexity
    isn't. [FIXME: State best, average, and worst-case time complexities here.]

    >>> a = [50, 90, 60, 40, 10, 80, 20, 30, 70]
    >>> [select_by_partitioning(a, i) for i in range(9)]
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> select_by_partitioning(a, -1)
    Traceback (most recent call last):
      ...
    IndexError: order statistic out of range
    >>> select_by_partitioning(a, 9)
    Traceback (most recent call last):
      ...
    IndexError: order statistic out of range
    >>> a
    [50, 90, 60, 40, 10, 80, 20, 30, 70]

    >>> b = [4.0, 1.0, 3, 2.0, True, 4, 1, 3.0]
    >>> [select_by_partitioning(b, i) for i in range(8)]
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]
    >>> b
    [4.0, 1.0, 3, 2.0, True, 4, 1, 3.0]
    """
    if not 0 <= k < len(values):
        raise IndexError('order statistic out of range')

    lower, similar, higher = partition_three(values, random.choice(values))

    if k < len(lower):
        return select_by_partitioning(lower, k)

    if k < len(lower) + len(similar):
        return similar[k - len(lower)]

    return select_by_partitioning(higher, k - (len(lower) + len(similar)))


# TODO: Rename this after the "select by partitioning" algorithm it implements.
def select_by_partitioning_iterative(values, k):
    """
    Nonrecursively find the stable kth order statistic or raise IndexError.

    This is like select_by_partitioning but iterative instead of recursive.

    >>> a = [50, 90, 60, 40, 10, 80, 20, 30, 70]
    >>> [select_by_partitioning_iterative(a, i) for i in range(9)]
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> select_by_partitioning_iterative(a, -1)
    Traceback (most recent call last):
      ...
    IndexError: order statistic out of range
    >>> select_by_partitioning_iterative(a, 9)
    Traceback (most recent call last):
      ...
    IndexError: order statistic out of range
    >>> a
    [50, 90, 60, 40, 10, 80, 20, 30, 70]

    >>> b = [4.0, 1.0, 3, 2.0, True, 4, 1, 3.0]
    >>> [select_by_partitioning_iterative(b, i) for i in range(8)]
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]
    >>> b
    [4.0, 1.0, 3, 2.0, True, 4, 1, 3.0]
    """
    if not 0 <= k < len(values):
        raise IndexError('order statistic out of range')

    while True:
        lower, similar, higher = partition_three(values, random.choice(values))

        if len(lower) <= k < len(lower) + len(similar):
            return similar[k - len(lower)]

        if k < len(lower):
            values = lower
        else:
            values = higher
            k -= len(lower) + len(similar)


def _do_stable_quicksort(values, choose_pivot):
    """Stable quicksort taking a function to choose a pivot from a sequence."""
    if len(values) < 2:
        return values

    lower, similar, higher = partition_three(values, choose_pivot(values))
    sorted_lower = _do_stable_quicksort(lower, choose_pivot)
    sorted_higher = _do_stable_quicksort(higher, choose_pivot)
    return sorted_lower + similar + sorted_higher

# TODO: Rename this after the "sort by partitioning" algorithm it implements.
def sort_by_partitioning_simple(values):
    """
    Stably sort values by a partition-based technique, creating a new list.

    This does most of its work in calls to partition_three. Average time
    complexity is asymptotically optimal. (What is the asymptotically optimal
    average-case time complexity for a comparison sort?) But worst-case time
    complexity isn't.
    [FIXME: State best, average, and worst-case time complexities here.]

    >>> sort_by_partitioning_simple([50, 90, 60, 40, 10, 80, 20, 30, 70])
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> sort_by_partitioning_simple([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0])
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]

    The average time complexity is good, but some common inputs may give
    worst-case time and/or fail with RecursionError. Ensure this doesn't happen
    for input that is all or almost all monotone in the same direction.
    FIXME: Then enable these tests:

    >>> r1 = range(50_000)
    >>> sort_by_partitioning_simple(r1) == list(r1)  # doctest: +SKIP
    True
    >>> r2 = range(49_999, -1, -1)
    >>> sort_by_partitioning_simple(r2) == list(r1)  # doctest: +SKIP
    True
    """
    return _do_stable_quicksort(list(values), lambda seq: seq[len(seq) // 2])


# TODO: Rename this after the "sort by partitioning" algorithm it implements.
def sort_by_partitioning(values):
    """
    Stably sort untrusted values by a partition-based technique, creating a new
    list.

    This is like sort_by_partitioning_simple, but naturally occurring patterns
    in the input, including combinations of sorted and reverse-sorted runs, are
    unlikely to cause worst-case performance or RecursionError. Also, it should
    be challenging (albeit potentially feasible) even for an expert attacker
    with full knowledge of this code and all its dependencies to craft input
    that causes degraded performance or excessive recursion depth. (Code that
    fails to do this might still pass all the currently written tests.)

    Feel free to use any standard library facilities other than those that have
    to do with sorting. Make sure this is still fundamentally the same
    algorithm as in sort_by_partitioning_simple.

    FIXME: After completing this, take another look at select_by_partitioning
    and select_by_partitioning_iterative. Do they suffer the same weakness as
    sort_by_partitioning_simple? If so, fix them analogously to the way you
    fixed it here. If not, add a brief paragraph to select_by_partitioning's
    docstring explaining why not.

    >>> sort_by_partitioning([50, 90, 60, 40, 10, 80, 20, 30, 70])
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> sort_by_partitioning([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0])
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]
    >>> r1 = range(50_000)
    >>> sort_by_partitioning(r1) == list(r1)
    True
    >>> r2 = range(49_999, -1, -1)
    >>> sort_by_partitioning(r2) == list(r1)
    True
    """
    return _do_stable_quicksort(list(values), random.choice)


# FIXME: This is the third of three similar implementations. Extract most or
#        all of their shared logic to a module-level nonpublic function.
#
# TODO: Rename this after the "sort by partitioning" algorithm it implements.
#
def sort_by_partitioning_hardened(values):
    """
    Stably sort seriously untrusted values by a partition-based technique,
    creating a new list.

    This is like sort_by_partitioning, but it should be infeasible even for a
    team of expert attackers with full knowledge of the code and all its
    dependencies and effectively unlimited time and money to craft input that
    causes degraded performance or excessive recursion depth--even though such
    input is guaranteed possible--except by exploiting a vulnerability in the
    platform. (Their best shot might be a vulnerability in the OS or hardware.)

    The hardening measures you take must leave best, average, and worst-case
    asymptotic time complexity unchanged. However, they will introduce
    substantial constant factors, so this implementation is likely ill-suited
    to real-world use, especially considering that anyone who wants these
    benefits can just use mergesort instead, which is worst-case O(n log n).

    [FIXME: Yet "sort by partitioning" is often preferred to mergesort! Briefly
    state, somewhere, the relevant difference between (a) our implementations
    of this algorithm and (b) the way it's usually done in production. Hint:
    The variations used in production lack an often-desired feature ours have:
    stability. What does lifting the stability requirement buy them?]

    >>> sort_by_partitioning_hardened([50, 90, 60, 40, 10, 80, 20, 30, 70])
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> sort_by_partitioning_hardened([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0])
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]
    >>> r1 = range(50_000)
    >>> sort_by_partitioning_hardened(r1) == list(r1)
    True
    >>> r2 = range(49_999, -1, -1)
    >>> sort_by_partitioning_hardened(r2) == list(r1)
    True
    """
    return _do_stable_quicksort(list(values), secrets.choice)


def partition_two_in_place(values, low, high, predicate):
    """
    Partition values[low:high] in-place 2-ways, by a predicate. Unstable.

    Values that satisfy the predicate are moved before those that don't. The
    index to the first non-satisfying value is returned. If all values in
    values[low:high] satisfy the predicate, high is returned.

    This is like std::partition in C++.

    >>> def test(values, low, high, predicate):
    ...     p = partition_two_in_place(values, low, high, predicate)
    ...     return p, sorted(values[low:p]), sorted(values[p:high])

    >>> test([], 0, 0, lambda: True)
    (0, [], [])
    >>> test([], 0, 0, lambda: False)
    (0, [], [])
    >>> test(['a'], 0, 1, str.islower)
    (1, ['a'], [])
    >>> test(['a'], 0, 1, str.isupper)
    (0, [], ['a'])
    >>> test(list('AbRaCaDABrA'), 0, 11, str.islower)
    (4, ['a', 'a', 'b', 'r'], ['A', 'A', 'A', 'B', 'C', 'D', 'R'])
    >>> test(list('AbRaCaDABrA'), 0, 11, str.isupper)
    (7, ['A', 'A', 'A', 'B', 'C', 'D', 'R'], ['a', 'a', 'b', 'r'])
    >>> test(list(range(99, -1, -1)), 55, 65, lambda x: x % 2 == 0)
    (60, [36, 38, 40, 42, 44], [35, 37, 39, 41, 43])
    """
    # This is a variant of the Hoare partition algorithm.
    # values[original_low:low] are the known satisfying elements.
    # values[low:high] are the not yet examined elements.
    # values[high:original_high] are the known non-satisfying elements.
    while low < high:
        if predicate(values[low]):
            low += 1
        elif predicate(values[high - 1]):
            values[low], values[high - 1] = values[high - 1], values[low]
            low += 1
            high -= 1
        else:
            high -= 1

    return high


# !!FIXME: When removing implementation bodies, remove this too.
PartIndices = collections.namedtuple('PartIndices', ('left', 'right'))

PartIndices.__doc__ = """Indices returned by 3-way in-place partitioning."""


def partition_three_in_place_rough(values, low, high, pivot):
    """
    Rearrange values[low:high] in place to be 3-way partitioned by a pivot.

    This is like partition_three, but it mutates its input instead of returning
    a new list, and it is unstable. It returns a named tuple of left and right,
    such that values[left:right] are the items neither less nor greater than
    the pivot. Auxiliary space complexity is O(1); this really is an in-place
    algorithm. See the note in partition_three on single vs. dual pivot 3-way
    partitioning.

    The asymptotic time complexity is the best possible for this problem.
    [FIXME: Note it here. Does being in-place worsen the time complexity?] But
    this is a first working approach, which may be slower by a constant factor
    than the algorithm in partition_three_in_place below. The algorithm here
    may seem clunky. Maybe it even feels a little bit cheaty.

    >>> def test(values, low, high, pivot):
    ...     p, q = partition_three_in_place_rough(values, low, high, pivot)
    ...     return sorted(values[low:p]), values[p:q], sorted(values[q:high])
    >>> test([], 0, 0, 'hi')
    ([], [], [])
    >>> test(['hj'], 0, 1, 'hi')
    ([], [], ['hj'])
    >>> test([7, 7, 1, 5, 6, 3, 6, 4, 2, 5, 9, 4, 8, 5, 3], 0, 15, 5)
    ([1, 2, 3, 3, 4, 4], [5, 5, 5], [6, 6, 7, 7, 8, 9])
    >>> test(['c', 'a', 'c', 'b', 'e', 'd'], 1, 4, 'c')
    (['a', 'b'], ['c'], [])
    >>> values = list(range(100, 0, -1)) * 10
    >>> partition_three_in_place_rough(values, 0, 1000, 42)
    PartIndices(left=410, right=420)
    >>> isinstance(_, tuple)
    True
    """
    left = partition_two_in_place(values, low, high, lambda lhs: lhs < pivot)

    right = partition_two_in_place(values, left, high,
                                   lambda lhs: not lhs > pivot)

    return PartIndices(left, right)


def partition_three_in_place(values, low, high, pivot):
    """
    Rearrange values[low:high] in place to be 3-way partitioned by a pivot.

    This is like partition_three, but it mutates its input instead of returning
    a new list, and it is unstable. It returns a named tuple of left and right,
    such that values[left:right] are the items neither less nor greater than
    the pivot. Auxiliary space complexity is O(1); this really is an in-place
    algorithm. See the note in partition_three on single vs. dual pivot 3-way
    partitioning.

    The asymptotic time complexity is [FIXME: note it here, too]. But compared
    to partition_three_in_place_rough, this is a more polished, different
    algorithm, which may be faster by a constant factor.

    >>> def test(values, low, high, pivot):
    ...     p, q = partition_three_in_place(values, low, high, pivot)
    ...     return sorted(values[low:p]), values[p:q], sorted(values[q:high])
    >>> test([], 0, 0, 'hi')
    ([], [], [])
    >>> test(['hj'], 0, 1, 'hi')
    ([], [], ['hj'])
    >>> test([7, 7, 1, 5, 6, 3, 6, 4, 2, 5, 9, 4, 8, 5, 3], 0, 15, 5)
    ([1, 2, 3, 3, 4, 4], [5, 5, 5], [6, 6, 7, 7, 8, 9])
    >>> test(['c', 'a', 'c', 'b', 'e', 'd'], 1, 4, 'c')
    (['a', 'b'], ['c'], [])
    >>> values = list(range(100, 0, -1)) * 10
    >>> partition_three_in_place(values, 0, 1000, 42)
    PartIndices(left=410, right=420)
    >>> isinstance(_, tuple)
    True
    """
    # values[original_low:low] are the known lesser elements.
    # values[low:current] are the known similar elements.
    # values[current:high] are the not yet examined elements.
    # values[high:original_high] are the known greater elements.
    current = low
    while current != high:
        if values[current] < pivot:
            values[low], values[current] = values[current], values[low]
            low += 1
            current += 1
        elif pivot < values[current]:
            high -= 1
            values[current], values[high] = values[high], values[current]
        else:
            current += 1

    return PartIndices(low, high)


def _do_quickselect(values, low, high, k):
    """Recursively find a kth order statistic, looking in values[low:high]."""
    if not low <= k < high:
        raise IndexError('order statistic out of range')

    pivot = values[random.randrange(low, high)]
    left, right = partition_three_in_place(values, low, high, pivot)

    if k < left:
        return _do_quickselect(values, low, left, k)
    if k < right:
        return values[k]
    return _do_quickselect(values, right, high, k)


# TODO: Rename this after the "select by partitioning" algorithm it implements.
def select_by_partitioning_in_place(values, k):
    """
    Rearrange values to be partitioned by the new values[k]. Return that value.

    This recursive implementation is like select_by_partitioning, but it
    mutates its input instead of returning a solution. It is unstable. It uses
    partition_three_in_place. This is in-place in the sense of average
    auxiliary space being asymptotically less then len(values). [FIXME: State
    the best, average, and worst-case time and auxiliary space complexities.]

    Like select_by_partitioning and sort_by_partitioning, this resists
    degrading to worst-case behavior for naturally data, and it would be
    challenging (albeit potentially feasible) for an expert attacker to craft
    such input.

    This is like std::nth_element in C++.

    >>> a = [50, 90, 60, 40, 10, 80, 20, 30, 70]
    >>> [select_by_partitioning_in_place(a[:], i) for i in range(9)]
    [10, 20, 30, 40, 50, 60, 70, 80, 90]

    >>> def test(values, k):
    ...     x = select_by_partitioning_in_place(values, k)
    ...     result = 'OK' if x is values[k] else f'{x!r} is not {values[k]!r}'
    ...     left = [(x if x < y else 'OK') for y in values[:k]]
    ...     right = [(z if z < x else 'OK') for z in values[k + 1:]]
    ...     print(f'{k=}, {result=!s}, {left=}, {right=}')

    >>> for k in range(8):
    ...     test([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0], k)
    k=0, result=OK, left=[], right=['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK']
    k=1, result=OK, left=['OK'], right=['OK', 'OK', 'OK', 'OK', 'OK', 'OK']
    k=2, result=OK, left=['OK', 'OK'], right=['OK', 'OK', 'OK', 'OK', 'OK']
    k=3, result=OK, left=['OK', 'OK', 'OK'], right=['OK', 'OK', 'OK', 'OK']
    k=4, result=OK, left=['OK', 'OK', 'OK', 'OK'], right=['OK', 'OK', 'OK']
    k=5, result=OK, left=['OK', 'OK', 'OK', 'OK', 'OK'], right=['OK', 'OK']
    k=6, result=OK, left=['OK', 'OK', 'OK', 'OK', 'OK', 'OK'], right=['OK']
    k=7, result=OK, left=['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK'], right=[]
    """
    return _do_quickselect(values, 0, len(values), k)


def _do_quickselect_iterative(values, low, high, k):
    """Iteratively find a kth order statistic, looking for values[low:high]."""
    if not low <= k < high:
        raise IndexError('order statistic out of range')

    while True:
        pivot = values[random.randrange(low, high)]
        left, right = partition_three_in_place(values, low, high, pivot)

        if left <= k < right:
            return values[k]

        if k < left:
            high = left
        else:
            low = right


# TODO: Rename this after the "select by partitioning" algorithm it implements.
def select_by_partitioning_in_place_iterative(values, k):
    """
    Rearrange values to be partitioned by the new values[k]. Return that value.

    This is like select_by_partitioning_in_place, but no recursion is used.

    [FIXME: State the best, average, and worst-case time and auxiliary space
    complexities, and explain why they are, or are not, all the same as those
    of the recursive select_by_partitioning_in_place.]

    >>> a = [50, 90, 60, 40, 10, 80, 20, 30, 70]
    >>> [select_by_partitioning_in_place_iterative(a[:], i) for i in range(9)]
    [10, 20, 30, 40, 50, 60, 70, 80, 90]

    >>> def test(values, k):
    ...     x = select_by_partitioning_in_place_iterative(values, k)
    ...     result = 'OK' if x is values[k] else f'{x!r} is not {values[k]!r}'
    ...     left = [(x if x < y else 'OK') for y in values[:k]]
    ...     right = [(z if z < x else 'OK') for z in values[k + 1:]]
    ...     print(f'{k=}, {result=!s}, {left=}, {right=}')

    >>> for k in range(8):
    ...     test([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0], k)
    k=0, result=OK, left=[], right=['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK']
    k=1, result=OK, left=['OK'], right=['OK', 'OK', 'OK', 'OK', 'OK', 'OK']
    k=2, result=OK, left=['OK', 'OK'], right=['OK', 'OK', 'OK', 'OK', 'OK']
    k=3, result=OK, left=['OK', 'OK', 'OK'], right=['OK', 'OK', 'OK', 'OK']
    k=4, result=OK, left=['OK', 'OK', 'OK', 'OK'], right=['OK', 'OK', 'OK']
    k=5, result=OK, left=['OK', 'OK', 'OK', 'OK', 'OK'], right=['OK', 'OK']
    k=6, result=OK, left=['OK', 'OK', 'OK', 'OK', 'OK', 'OK'], right=['OK']
    k=7, result=OK, left=['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK'], right=[]
    """
    return _do_quickselect_iterative(values, 0, len(values), k)


def median_by_sorting(values):
    """
    Given a sequence of numbers, find the median by sorting the values.

    This calls only builtins. It runs in best case O(n), average and worst case
    O(n log n) time. Do not modify the original input.

    >>> median_by_sorting([2, 11, 14, 10, 9, 3, 8, 5, 12, 0, 6, 13, 4, 7, 1])
    7
    >>> median_by_sorting([13, 0.2, 8, 5, 8.9, 6, 1, 11, 2, 3, 7, 12.4, 10, 3])
    6.5
    >>> median_by_sorting((4, 1.3, 8, 7, 9, 2, 0.5))
    4
    """
    dup = sorted(values)
    mid = len(dup) // 2
    return (dup[mid - 1] + dup[mid]) / 2 if len(dup) % 2 == 0 else dup[mid]


def median(values):
    """
    Given a sequence, find the median by [FIXME: briefly state how this works].

    Sorting is not used. Other than builtins, this may only call one of:

      - select_by_partitioning
      - select_by_partitioning_iterative
      - select_by_partitioning_in_place
      - select_by_partitioning_in_place_iterative

    Which one it uses does not differ across calls. It is not recursive, except
    indirectly if the selection function it calls is recursive. A single call
    to this function results in at most one call to the selection function. It
    runs in [FIXME: state the best, average, and worst case time complexity],
    so this algorithm is often a reasonable choice for finding medians. Do not
    modify the original input.

    >>> median([2, 11, 14, 10, 9, 3, 8, 5, 12, 0, 6, 13, 4, 7, 1])
    7
    >>> median([13, 0.2, 8, 5, 8.9, 6, 1, 11, 2, 3, 7, 12.4, 10, 3])
    6.5
    >>> median((4, 1.3, 8, 7, 9, 2, 0.5))
    4
    """
    dup = list(values)
    mid = len(dup) // 2
    val = select_by_partitioning_in_place_iterative(dup, mid)
    return (max(dup[:mid]) + val) / 2 if len(dup) % 2 == 0 else val


def _do_quicksort_in_place(values, low, high, choose_pivot_index):
    """In-place recursive quicksort taking a pivot-index choosing function."""
    if high - low < 2:
        return

    pivot = values[choose_pivot_index(low, high)]
    left, right = partition_three_in_place(values, low, high, pivot)
    _do_quicksort_in_place(values, low, left, choose_pivot_index)
    _do_quicksort_in_place(values, right, high, choose_pivot_index)


# FIXME: As with the non-in-place "sort by partitioning" functions above, there
#        are 3 of these. Put most or all of these 3 functions' shared logic to
#        a module-level nonpublic function (specific to the in-place versions).
#
# TODO: Rename this after the "sort by partitioning" algorithm it implements.
#
def sort_by_partitioning_in_place_simple(values):
    """
    Sort values in place by a partition-based technique. Unstable.

    This does most of its work in calls to partition_three_in_place. Average
    time complexity as asymptotically optimal for a comparison sort. But worst
    case time complexity isn't. This is in-place in the sense of average
    auxiliary space being asymptotically less then len(values). [FIXME: State
    the best, average, and worst-case time and auxiliary space complexities.]

    As in sort_by_partitioning_simple, some common inputs may give worst-case
    time and/or fail with RecursionError, but rarely rising, or rarely falling,
    does not trigger this.

    >>> def test(a):
    ...     print(sort_by_partitioning_in_place_simple(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    >>> b = list(range(50_000))
    >>> sort_by_partitioning_in_place_simple(b)
    >>> b == list(range(50_000))
    True
    >>> c = list(range(49_999, -1, -1))
    >>> sort_by_partitioning_in_place_simple(c)
    >>> c == list(range(50_000))
    True
    """
    _do_quicksort_in_place(values, 0, len(values),
                           lambda low, high: (low + high) // 2)


# TODO: Rename this after the "sort by partitioning" algorithm it implements.
def sort_by_partitioning_in_place(values):
    """
    Sort untrusted values in place by a partition-based technique. Unstable.

    This is like sort_by_partitioning_simple, but naturally occurring patterns
    in the input, including combinations of sorted and reverse-sorted runs, are
    unlikely to cause worst-case performance or RecursionError. Also, it should
    be challenging (albeit potentially feasible) even for an expert attacker
    with full knowledge of this code and all its dependencies to craft input
    that causes degraded performance or excessive recursion depth.

    This has the same relation to sort_by_partitioning_in_place_simple that
    sort_by_partitioning has to sort_by_partitioning_simple.

    >>> def test(a): print(sort_by_partitioning_in_place(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    >>> b = list(range(50_000))
    >>> sort_by_partitioning_in_place(b)
    >>> b == list(range(50_000))
    True
    >>> c = list(range(49_999, -1, -1))
    >>> sort_by_partitioning_in_place(c)
    >>> c == list(range(50_000))
    True
    """
    _do_quicksort_in_place(values, 0, len(values), random.randrange)


# TODO: Rename this after the "sort by partitioning" algorithm it implements.
def sort_by_partitioning_in_place_hardened(values):
    """
    Sort seriously untrusted values in place by a partition-based technique.

    This is like sort_by_partitioning_in_place, but it should be as secure as
    possible against highly sophisticated deliberate crafting of input, so that
    nobody can deliberately cause it to degrade to worst-case performance,
    while still being "the same algorithm" as sort_by_partitioning_in_place.

    See sort_by_partitioning_hardened for a fuller description. This has the
    same relation to sort_by_partitioning_in_place that sort_by_partitioning
    has to sort_by_partitioning_hardened.

    >>> def test(a):
    ...     print(sort_by_partitioning_in_place_hardened(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    >>> b = list(range(50_000))
    >>> sort_by_partitioning_in_place_hardened(b)
    >>> b == list(range(50_000))
    True
    >>> c = list(range(49_999, -1, -1))
    >>> sort_by_partitioning_in_place_hardened(c)
    >>> c == list(range(50_000))
    True
    """
    _do_quicksort_in_place(values, 0, len(values),
                           lambda low, high: secrets.choice(range(low, high)))


# NOTE: This iterative implementation will not be able to share most of its
#       logic with the 3 recursive implementations that precede it, other than
#       how they, and it, all call partition_three_in_place for partitioning.
#
# TODO: Rename this after the "sort by partitioning" algorithm it implements.
#
def sort_by_partitioning_in_place_iterative(values):
    """
    Iteratively sort values in place by a partition-based technique. Unstable.

    This is like sort_by_partitioning_in_place (and the input is "untrusted" to
    the same extent as there, but not more), but no recursion is used.

    [FIXME: State the best, average, and worst-case time and auxiliary space
    complexities, and explain why they are, or are not, all the same as those
    of the recursive sort_by_partitioning_in_place.]

    [FIXME: The in-place version of this algorithm, implemented iteratively
    here, is easier to make iterative than (a) the non-in-place version of this
    algorithm, or (b) any version of top-down mergesort. (Unlike bottom-up
    mergesort, but like this algorithm, top-down mergesort is usually done
    recursively.) State what's special here, contrasting to both (a) and (b).]

    >>> def test(a):
    ...     print(sort_by_partitioning_in_place_iterative(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    >>> b = list(range(50_000))
    >>> sort_by_partitioning_in_place_iterative(b)
    >>> b == list(range(50_000))
    True
    >>> c = list(range(49_999, -1, -1))
    >>> sort_by_partitioning_in_place_iterative(c)
    >>> c == list(range(50_000))
    True
    """
    if len(values) < 2:
        return

    stack = [(0, len(values))]

    while stack:
        low, high = stack.pop()
        pivot = values[random.randrange(low, high)]
        left, right = partition_three_in_place(values, low, high, pivot)
        if high - right > 1:
            stack.append((right, high))
        if left - low > 1:
            stack.append((low, left))


def _do_safe_quicksort_in_place(values, low, high):
    """In-place stack-safe quicksort, recursing on just the short side."""
    while high - low > 1:
        pivot = values[random.randrange(low, high)]
        left, right = partition_three_in_place(values, low, high, pivot)

        if high - right < left - low:
            _do_safe_quicksort_in_place(values, right, high)
            high = left
        else:
            _do_safe_quicksort_in_place(values, low, left)
            low = right


# NOTE: This likewise will not be able to share most of its logic with any
#       other "sort by partitioning" implementations. But if you use a helper
#       function, it may still be clearer for it to be a module-level function.
#
# TODO: Rename this after the "sort by partitioning" algorithm it implements.
#
def sort_by_partitioning_in_place_safe(values):
    """
    Sort in place by a partition-based technique in O(log n) auxiliary space.

    This is an unstable sort closely based on sort_by_partitioning_in_place and
    with the same best, average, and worst-case time complexity. (Its input is
    "untrusted" to the same extent as there, but not more.) But this improved
    version has O(log n) worst-case auxiliary space complexity. So it's "safe"
    in the sense that even worst-case input doesn't cause excessive call depth.
    Like recursive mergesort, it's not prone to raising RecursionError.

    Furthermore, this never instantiates and uses its own list or other data
    structure: no new collections are created and, at all times, every variable
    either refers to the original input sequence or to an object that takes
    O(1) space. (This also applies to any helper functions.) The input sequence
    is not resized and no object originally absent from it is ever put in it.

    This doesn't rely on introspection or other dynamic Python features. It
    easily translates to C code (which doesn't use malloc or anything related).

    >>> def test(a): print(sort_by_partitioning_in_place_safe(a), a, sep='; ')
    >>> test([])
    None; []
    >>> test([10, 20])
    None; [10, 20]
    >>> test([20, 10])
    None; [10, 20]
    >>> test([3, 3])
    None; [3, 3]
    >>> test([5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129])
    None; [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> test(['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs'])
    None; ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    >>> b = list(range(50_000))
    >>> sort_by_partitioning_in_place_safe(b)
    >>> b == list(range(50_000))
    True
    >>> c = list(range(49_999, -1, -1))
    >>> sort_by_partitioning_in_place_safe(c)
    >>> c == list(range(50_000))
    True
    """
    _do_safe_quicksort_in_place(values, 0, len(values))


def stabilize(unstable_sort, *, materialize=False):
    """
    Create a stable sort from an unstable sort. Assume total ordering.

    This higher-order function takes any sorting function, permitted to be
    unstable, that accepts an iterable of comparable items and returns a sorted
    list. It returns a sorting function based on the given function, using
    conceptually almost the same algorithm, yet guaranteed to be stable. The
    output function may assume total ordering, but it must not reorder
    different objects that compare equal. It need not accept key= or reverse=
    arguments.

    The input function is required to be correct. The output function will then
    be both correct and stable, for the same reason the input function is
    correct, whatever reason that is. This is to say both functions "work the
    same." Asymptotic best, average, and worst-case time complexity shall
    usually be preserved (if not, the input function is rather strange). The
    output function may be slower than the input function by a constant factor.

    The output function's asymptotic space complexity is at most that of the
    input function or O(n), whichever is greater. However, it avoids doing
    extra materialization unless materialize=True, in which case the input
    function is only required to accept lists.

    The output function should be given metadata so @stabilize is suitable to
    use as a decorator. (Copy the metadata no matter how stabilize is called.)

    >>> import fractions, random

    >>> stabilized_selection_sort = stabilize(selection_sort)
    >>> stabilized_selection_sort([7, 3, 4, 6, 13, 5, 12, 14, 9, 10, 11, 8])
    [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>> stabilized_selection_sort([1, 1.0, True])
    [1, 1.0, True]
    >>> stabilized_selection_sort([1, 1.0, True, fractions.Fraction(1, 1)])
    [1, 1.0, True, Fraction(1, 1)]

    >>> @stabilize
    ... def restabilized_sorted(values):
    ...     dup = list(values)
    ...     random.shuffle(dup)  # Throw stability straight out the window.
    ...     dup.sort()
    ...     return dup
    >>> restabilized_sorted.__name__
    'restabilized_sorted'
    >>> restabilized_sorted([7, 3, 4, 6, 13, 5, 12, 14, 9, 10, 11, 8])
    [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>> restabilized_sorted([1, 1.0, True])
    [1, 1.0, True]
    >>> restabilized_sorted([1, 1.0, True, fractions.Fraction(1, 1)])
    [1, 1.0, True, Fraction(1, 1)]

    >>> isort = stabilize(insertion_sort_recursive_alt, materialize=True)
    >>> isort([7, 3, 4, 6, 13, 5, 12, 14, 9, 10, 11, 8])
    [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>> isort([1, 1.0, True])
    [1, 1.0, True]
    >>> isort([1, 1.0, True, fractions.Fraction(1, 1)])
    [1, 1.0, True, Fraction(1, 1)]
    """
    maybe_materialize = (list if materialize else lambda arg: arg)

    @functools.wraps(unstable_sort)
    def stabilized_sort(values):
        augmented_input = ((item, index) for index, item in enumerate(values))
        augmented_output = unstable_sort(maybe_materialize(augmented_input))
        return [item for item, _ in augmented_output]

    return stabilized_sort


def _dealias_other(keys, other):
    """Return other without the keys object or any repeated objects."""
    by_id = {id(other_seq): other_seq for other_seq in other}
    with contextlib.suppress(KeyError):
        del by_id[id(keys)]
    return tuple(by_id.values())


def _augmented_swap(keys, other, i, j):
    """Swap the i and j indexed elements in keys and in each other sequence."""
    keys[i], keys[j] = keys[j], keys[i]
    for other_seq in other:
        other_seq[i], other_seq[j] = other_seq[j], other_seq[i]


def _augmented_partition_three_in_place(keys, other, low, high, pivot):
    """
    Rearrange a[low:high], a=keys and each a in other, to be 3-way partitioned.

    This is like partition_three_in_place, but it is augmented, for use in
    augmented_sort_in_place (below). Objects in keys are compared to the pivot.
    No comparisons are done on objects in sequences in other. Those sequences
    are permuted in the same way that keys is permuted. This takes O(n k) time.
    """
    # keys[original_low:low] are the known lesser elements.
    # keys[low:current] are the known similar elements.
    # keys[current:high] are the not yet examined elements.
    # keys[high:original_high] are the known greater elements.
    current = low
    while current != high:
        if keys[current] < pivot:
            _augmented_swap(keys, other, low, current)
            low += 1
            current += 1
        elif pivot < keys[current]:
            high -= 1
            _augmented_swap(keys, other, current, high)
        else:
            current += 1

    return PartIndices(low, high)


def _do_augmented_safe_quicksort_in_place(keys, other, low, high):
    """Augmented stack-safe quicksort, recursing on just hte short side."""
    while high - low > 1:
        pivot = keys[random.randrange(low, high)]

        left, right = _augmented_partition_three_in_place(
            keys, other, low, high, pivot)

        if high - right < left - low:
            _do_augmented_safe_quicksort_in_place(keys, other, right, high)
            high = left
        else:
            _do_augmented_safe_quicksort_in_place(keys, other, low, left)
            low = right


def augmented_sort_in_place(keys, *other, alias=False):
    """
    Sort keys and rearrange zero or more other sequences accordingly, in place.

    The input is a sequence, keys, whose elements are to be compared, and zero
    or more sequences in other, each of the same length as keys, whose elements
    are never compared. The keys are rearranged by sorting, and also serve as
    keys for each of the other sequences, which must be rearranged the same
    way: if values is in other and the object at keys[i] ends up at keys[j],
    then the object at values[i] ends up at values[j]. Objects in the other
    sequences are never examined in any way (their references are read and
    written but not dereferenced).

    If and only if the alias keyword argument is true, the sequences may alias,
    meaning that any sequence, including keys itself, may appear any number of
    times in other. But if values1 and values2 are different sequence objects,
    you may still assume that assigning elements of values1 does not affect
    values2. (This is typically the case, and the caller must ensure it.)

    With n == len(keys) and k == len(other), this takes:

      - Average-case O(n k log n) time.
      - Worst-case O(k + log n) auxiliary space, if alias is True.
      - Worst-case O(log n) auxiliary space, if alias is False.

    FIXME: Needs tests.
    """
    good_other = _dealias_other(keys, other) if alias else other
    _do_augmented_safe_quicksort_in_place(keys, good_other, 0, len(keys))


def make_deep_tuple(depth):
    """Make a tuple of the specified depth."""
    tup = ()
    for _ in range(depth):
        tup = (tup,)
    return tup


def nest(seed, degree, height):
    """
    Create a nested tuple from a seed, branching degree, and height. Recursive.

    The seed will be a leaf or subtree.

    >>> nest('hi', 2, 0)
    'hi'
    >>> nest('hi', 2, 1)
    ('hi', 'hi')
    >>> nest('hi', 2, 2)
    (('hi', 'hi'), ('hi', 'hi'))
    >>> nest('hi', 2, 3)
    ((('hi', 'hi'), ('hi', 'hi')), (('hi', 'hi'), ('hi', 'hi')))
    >>> from pprint import pprint
    >>> pprint(nest('hi', 3, 3))
    ((('hi', 'hi', 'hi'), ('hi', 'hi', 'hi'), ('hi', 'hi', 'hi')),
     (('hi', 'hi', 'hi'), ('hi', 'hi', 'hi'), ('hi', 'hi', 'hi')),
     (('hi', 'hi', 'hi'), ('hi', 'hi', 'hi'), ('hi', 'hi', 'hi')))
    """
    if degree < 0:
        raise ValueError('degree cannot be negative')
    if height < 0:
        raise ValueError('height cannot be negative')
    return seed if height == 0 else nest((seed,) * degree, degree, height - 1)


def nest_iterative(seed, degree, height):
    """
    Create a nested tuple from a seed, branching degree, and height. Iterative.

    The seed will be a leaf or subtree.

    >>> nest_iterative('hi', 2, 0)
    'hi'
    >>> nest_iterative('hi', 2, 1)
    ('hi', 'hi')
    >>> nest_iterative('hi', 2, 2)
    (('hi', 'hi'), ('hi', 'hi'))
    >>> nest_iterative('hi', 2, 3)
    ((('hi', 'hi'), ('hi', 'hi')), (('hi', 'hi'), ('hi', 'hi')))
    >>> from pprint import pprint
    >>> pprint(nest_iterative('hi', 3, 3))
    ((('hi', 'hi', 'hi'), ('hi', 'hi', 'hi'), ('hi', 'hi', 'hi')),
     (('hi', 'hi', 'hi'), ('hi', 'hi', 'hi'), ('hi', 'hi', 'hi')),
     (('hi', 'hi', 'hi'), ('hi', 'hi', 'hi'), ('hi', 'hi', 'hi')))
    """
    if degree < 0:
        raise ValueError('degree cannot be negative')
    if height < 0:
        raise ValueError('height cannot be negative')

    for _ in range(height):
        seed = (seed,) * degree

    return seed


def observe_edge(parent, child):
    """
    Print a representation of an edge from parent to child in a tree.

    This is a simple edge observer. See the "..._observed" functions below.
    """
    print(f'{parent!r}  ->  {child!r}')


def flatten(root):
    """
    Recursively lazily flatten a nested tuple, yielding all non-tuple leaves.

    This returns an iterator that yields all leaves in the order the repr shows
    them. If root is not a tuple, it is considered to be the one and only leaf.

    >>> list(flatten(()))
    []
    >>> list(flatten(3))
    [3]
    >>> list(flatten([3]))
    [[3]]
    >>> list(flatten((3,)))
    [3]
    >>> list(flatten((2, 3, 7)))
    [2, 3, 7]
    >>> list(flatten((2, ((3,), 7))))
    [2, 3, 7]
    >>> root1 = (1, (2, (3, (4, (5, (6, (7, (8, (9,), (), 10)), 11))), 12)))
    >>> list(flatten(root1))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> root2 = ('foo', ['bar'], ('baz', ['quux', ('foobar',)]))
    >>> list(flatten(root2))
    ['foo', ['bar'], 'baz', ['quux', ('foobar',)]]
    >>> list(flatten(nest('hi', 3, 3))) == ['hi'] * 27
    True
    """
    # base case: we are at a leaf
    if not isinstance(root, tuple):
        yield root
        return

    for element in root:
        yield from flatten(element)


def flatten_observed(root, observer):
    """
    Recursively lazily flatten a nested tuple. Call an observer for each edge.

    This is like flatten (above), but it also calls observer(parent, child) for
    each child found, in the order they are found.

    >>> list(flatten_observed((), observe_edge))
    []
    >>> list(flatten_observed(({()},), observe_edge))
    ({()},)  ->  {()}
    [{()}]
    >>> root3 = ((1, (2,), 3), (4, (5,), (), 6))
    >>> list(flatten_observed(root3, observe_edge))
    ((1, (2,), 3), (4, (5,), (), 6))  ->  (1, (2,), 3)
    (1, (2,), 3)  ->  1
    (1, (2,), 3)  ->  (2,)
    (2,)  ->  2
    (1, (2,), 3)  ->  3
    ((1, (2,), 3), (4, (5,), (), 6))  ->  (4, (5,), (), 6)
    (4, (5,), (), 6)  ->  4
    (4, (5,), (), 6)  ->  (5,)
    (5,)  ->  5
    (4, (5,), (), 6)  ->  ()
    (4, (5,), (), 6)  ->  6
    [1, 2, 3, 4, 5, 6]
    """
    # base case: we are at a leaf
    if not isinstance(root, tuple):
        yield root
        return

    for element in root:
        observer(root, element)
        yield from flatten_observed(element, observer)


def flatten_iterative(root):
    """
    Nonrecursively lazily flatten a tuple, yielding all non-tuple leaves.

    This is like flatten (above), but using a purely iterative algorithm.

    >>> list(flatten_iterative(()))
    []
    >>> list(flatten_iterative(3))
    [3]
    >>> list(flatten_iterative([3]))
    [[3]]
    >>> list(flatten_iterative((3,)))
    [3]
    >>> list(flatten_iterative((2, 3, 7)))
    [2, 3, 7]
    >>> list(flatten_iterative((2, ((3,), 7))))
    [2, 3, 7]
    >>> root1 = (1, (2, (3, (4, (5, (6, (7, (8, (9,), (), 10)), 11))), 12)))
    >>> list(flatten_iterative(root1))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    >>> root2 = ('foo', ['bar'], ('baz', ['quux', ('foobar',)]))
    >>> list(flatten_iterative(root2))
    ['foo', ['bar'], 'baz', ['quux', ('foobar',)]]
    >>> list(flatten_iterative(nest('hi', 3, 3))) == ['hi'] * 27
    True
    """
    stack = [root]

    while stack:
        element = stack.pop()
        if isinstance(element, tuple):
            stack.extend(reversed(element))
        else:
            yield element


def flatten_iterative_observed(root, observer):
    """
    Nonrecursively lazily flatten a tuple. Call an observer for each edge.

    This is like flatten_iterative (above), but it also calls
    observer(parent, child) for each child found, in the order the usual
    recursive algorithm (implemented in flatten, above) would find them.

    Various iterative algorithms discover nodes in different orders. There are
    no requirements on the order in which the algorithm used here discovers
    nodes, so long as the observer can't tell this apart from flatten_observed.

    [But you should also look at the order the nodes are really discovered in.]

    >>> list(flatten_iterative_observed((), observe_edge))
    []
    >>> list(flatten_iterative_observed(({()},), observe_edge))
    ({()},)  ->  {()}
    [{()}]
    >>> root3 = ((1, (2,), 3), (4, (5,), (), 6))
    >>> list(flatten_iterative_observed(root3, observe_edge))
    ((1, (2,), 3), (4, (5,), (), 6))  ->  (1, (2,), 3)
    (1, (2,), 3)  ->  1
    (1, (2,), 3)  ->  (2,)
    (2,)  ->  2
    (1, (2,), 3)  ->  3
    ((1, (2,), 3), (4, (5,), (), 6))  ->  (4, (5,), (), 6)
    (4, (5,), (), 6)  ->  4
    (4, (5,), (), 6)  ->  (5,)
    (5,)  ->  5
    (4, (5,), (), 6)  ->  ()
    (4, (5,), (), 6)  ->  6
    [1, 2, 3, 4, 5, 6]
    """
    stack = [(None, root)]

    while stack:
        parent, element = stack.pop()
        if parent is not None:
            observer(parent, element)

        if isinstance(element, tuple):
            stack.extend((element, child) for child in reversed(element))
        else:
            yield element


def flatten_levelorder(root):
    """
    Lazily flatten a tuple in breadth-first order (level order).

    This is like flatten and flatten_iterative (above), but those flatten in
    depth-first order. In contrast, this function yields leaves closer to the
    root before yielding leaves farther from the root. The same leaves are all
    eventually yielded, but often in a different order.

    Leaves at the same level are yielded in the same relative order flatten and
    flatten_iterative yields them: left to right.

    >>> list(flatten_levelorder(()))
    []
    >>> list(flatten_levelorder(3))
    [3]
    >>> list(flatten_levelorder([3]))
    [[3]]
    >>> list(flatten_levelorder((3,)))
    [3]
    >>> list(flatten_levelorder((2, 3, 7)))
    [2, 3, 7]
    >>> list(flatten_levelorder((2, ((3,), 7))))
    [2, 7, 3]
    >>> root1 = (1, (2, (3, (4, (5, (6, (7, (8, (9,), (), 10)), 11))), 12)))
    >>> list(flatten_levelorder(root1))
    [1, 2, 3, 12, 4, 5, 6, 11, 7, 8, 10, 9]
    >>> root2 = ('foo', ['bar'], ('baz', ['quux', ('foobar',)]))
    >>> list(flatten_levelorder(root2))
    ['foo', ['bar'], 'baz', ['quux', ('foobar',)]]
    >>> list(flatten_levelorder(nest('hi', 3, 3))) == ['hi'] * 27
    True
    """
    queue = collections.deque((root,))

    while queue:
        element = queue.popleft()
        if isinstance(element, tuple):
            queue.extend(element)
        else:
            yield element


def flatten_levelorder_observed(root, observer):
    """
    Lazily flatten a tuple breadth-first. Call an observer for each edge.

    This is like flatten_levelorder (above), but it also calls
    observer(parent, child) for each child found, in the order they are found.

    NOTE: The code here can be simpler than in flatten_iterative_observed.

    >>> list(flatten_levelorder_observed((), observe_edge))
    []
    >>> list(flatten_levelorder_observed(({()},), observe_edge))
    ({()},)  ->  {()}
    [{()}]
    >>> root3 = ((1, (2,), 3), (4, (5,), (), 6))
    >>> list(flatten_levelorder_observed(root3, observe_edge))
    ((1, (2,), 3), (4, (5,), (), 6))  ->  (1, (2,), 3)
    ((1, (2,), 3), (4, (5,), (), 6))  ->  (4, (5,), (), 6)
    (1, (2,), 3)  ->  1
    (1, (2,), 3)  ->  (2,)
    (1, (2,), 3)  ->  3
    (4, (5,), (), 6)  ->  4
    (4, (5,), (), 6)  ->  (5,)
    (4, (5,), (), 6)  ->  ()
    (4, (5,), (), 6)  ->  6
    (2,)  ->  2
    (5,)  ->  5
    [1, 3, 4, 6, 2, 5]
    """
    queue = collections.deque((root,))

    while queue:
        element = queue.popleft()
        if isinstance(element, tuple):
            for subelement in element:
                observer(element, subelement)
            queue.extend(element)
        else:
            yield element


def leaf_sum(root):
    """
    Using recursion, sum non-tuples accessible through nested tuples.

    Overlapping subproblems (the same tuple object in multiple places) are
    solved only once; the solution is cached and reused.

    >>> leaf_sum(3)
    3
    >>> leaf_sum(())
    0
    >>> root = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
    >>> leaf_sum(root)
    57
    >>> leaf_sum(nest(seed=1, degree=2, height=200))
    1606938044258990275541962092341162602522202993782792835301376
    >>> from fibonacci import fib, fib_nest
    >>> leaf_sum(fib_nest(10))
    55
    >>> all(leaf_sum(fib_nest(i)) == x for i, x in zip(range(401), fib()))
    True
    """
    cache = {}

    def traverse(parent):
        if not isinstance(parent, tuple):
            return parent

        if id(parent) not in cache:
            cache[id(parent)] = sum(traverse(child) for child in parent)

        return cache[id(parent)]

    return traverse(root)


def _traverse(parent, cache):
    """Traverse the tree for leaf_sum_alt."""
    if not isinstance(parent, tuple):
        return parent

    if id(parent) not in cache:
        cache[id(parent)] = sum(_traverse(child, cache) for child in parent)

    return cache[id(parent)]


def leaf_sum_alt(root):
    """
    Using recursion, sum non-tuples accessible through nested tuples.

    Overlapping subproblems (the same tuple object in multiple places) are
    solved only once; the solution is cached and reused.

    This is like leaf_sum except it does not use any local functions.

    >>> leaf_sum_alt(3)
    3
    >>> leaf_sum_alt(())
    0
    >>> root = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
    >>> leaf_sum_alt(root)
    57
    >>> leaf_sum_alt(nest(seed=1, degree=2, height=200))
    1606938044258990275541962092341162602522202993782792835301376
    >>> from fibonacci import fib, fib_nest
    >>> leaf_sum_alt(fib_nest(10))
    55
    >>> all(leaf_sum_alt(fib_nest(i)) == x for i, x in zip(range(401), fib()))
    True
    """
    cache = {}
    return _traverse(root, cache)


def leaf_sum_dec(root):
    """
    Using recursion, sum non-tuples accessible through nested tuples.

    Overlapping subproblems (the same tuple object in multiple places) are
    solved only once; the solution is cached and reused.

    This is like leaf_sum (and leaf_sum_alt), but @decorators.memoize_by is
    used for memoization, which is safe for the same reason the sums table
    works in leaf_sum: a tuple structure (i.e., one where only leaves are
    permitted to be non-tuples) is ineligible for garbage collection as long as
    its root is accessible. This holds even in the presence of concurrency
    considerations, since tuples are immutable.

    Note that it would not be safe to cache calls to the top-level function
    leaf_sum_dec by id. This must go on the helper function, since nothing can
    be assumed about lifetime of objects across top-level calls.

    >>> leaf_sum_dec(3)
    3
    >>> leaf_sum_dec(())
    0
    >>> root = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
    >>> leaf_sum_dec(root)
    57
    >>> leaf_sum_dec(nest(seed=1, degree=2, height=200))
    1606938044258990275541962092341162602522202993782792835301376
    >>> from fibonacci import fib, fib_nest
    >>> leaf_sum_dec(fib_nest(10))
    55
    >>> all(leaf_sum_dec(fib_nest(i)) == x for i, x in zip(range(401), fib()))
    True
    """
    @decorators.memoize_by(id)
    def traverse(parent):
        if not isinstance(parent, tuple):
            return parent

        return sum(traverse(child) for child in parent)

    return traverse(root)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
