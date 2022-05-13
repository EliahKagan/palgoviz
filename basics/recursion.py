#!/usr/bin/env python

"""
Some recursion examples (and a few related iterative implementations).

See also object_graph.py.
"""

import bisect
import collections
import functools
import operator
import queues
import random
import secrets

import decorators


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


def selection_sort(values):
    """
    Sort by repeatedly finding minimum or maximum values, creating a new list.

    Most selection sort implementations, including this one, are unstable. That
    lets them be significantly simpler and also faster by a constant factor.

    [FIXME: Write best, average, and worst case asymptotic time complexities.]

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


def select_k_left_unstable(values, k):
    """
    Find some kth order statistic (0-based indexing) in O(k * n) time.

    This is an object that appears at index k in some sorted permutation of the
    values. This could be the same object sorted(values)[k] but it need not be.
    In the required time complexity, n == len(values).

    Actually evaluating sorted(values)[k] would often be faster than this, but
    too slow for small k (too slow when k grows slower than log n). The logic
    here should be directly based on selection sort. Do not modify values.

    It is possible to solve this (and select_k_right below) in O(k log n)
    worst-case time with another technique, but this exercise isn't about that.

    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> [select_k_left_unstable(a, i) for i in range(len(a))]
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> a
    [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    """
    dup = list(values)

    def extract_min():
        index, _ = min(enumerate(dup), key=operator.itemgetter(1))
        dup[index], dup[-1] = dup[-1], dup[index]
        return dup.pop()

    for _ in range(k):
        extract_min()

    return extract_min()


def select_k_right_unstable(values, k):
    """
    Find some kth order statistic (0-based indexing) in O(k * (n - k)) time.

    See select_k_left above. Here, actually evaluating sorted(values(k)) would
    be too slow when k is almost n (when n - k grows slower than log n).

    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> [select_k_right_unstable(a, i) for i in range(len(a))]
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    >>> a
    [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    """
    dup = list(values)

    def extract_max():
        index, _ = max(enumerate(dup), key=operator.itemgetter(1))
        dup[index], dup[-1] = dup[-1], dup[index]
        return dup.pop()

    for _ in range(len(dup) - k - 1):
        extract_max()

    return extract_max()


def select_k_right_unstable_alt(values, k):
    """
    Find some kth order statistic (0-based indexing) in O(k * (n - k)) time.

    This alternate implementation of select_k_right_unstable makes good use of
    a data structure already implemented in another module of this project.

    >>> a = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
    >>> [select_k_right_unstable_alt(a, i) for i in range(len(a))]
    [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]
    """
    pq = queues.FastEnqueueMaxPriorityQueue()
    for value in values:
        pq.enqueue(value)

    right_k = len(pq) - k - 1
    for _ in range(right_k):
        pq.dequeue()

    return pq.dequeue()


def merge_two_slow(values1, values2):
    """
    Return a sorted list that that takes two sorted sequences as input.

    If values2 is empty, this is equivalent to a binary insertion sort.

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
    Return a sorted list that that takes two sorted sequences as input.

    If values2 is empty, this is equivalent to a binary insertion sort.

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
    Return a sorted list that that takes two sorted sequences as input.

    If values2 is empty, this is equivalent to a binary insertion sort.

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


def partition3(values, pivot):
    """
    Stable 3-way partition.

    Returns lists of values less than, similar to, and greater than the pivot.

    >>> partition3([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0], 4)
    ([3, -17, 1, 2, -15, 1, -1, 0], [4], [5, 8, 66, 9, 5, 8])
    >>> partition3([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0], 5)
    ([3, -17, 1, 4, 2, -15, 1, -1, 0], [5, 5], [8, 66, 9, 8])
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

    return lower, similar, higher


def similar_range(values, new_value):
    """
    Find the range of valid insertion points for new_value in sorted(values).

    (When new_value is already present in values, this is the same as the range
    of indices where new_value could appear in an arbitrary sorted permutation
    of values, i.e., in a sorting of values without any stability guarantee.)

    The asymptotic time complexity is the best possible for this problem:
    [FIXME: Note it here.]

    See also similar_range_alt below.

    >>> similar_range([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0], 4)
    range(8, 9)
    >>> similar_range([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0], 5)
    range(9, 11)
    """
    lower, similar, _ = partition3(values, new_value)
    return range(len(lower), len(lower) + len(similar))


def similar_range_alt(values, new_value):
    """
    Find the range of valid insertion points for new_value in sorted(values).

    This is an alternate implementation of similar_range. One uses partition3
    for all but O(1) of its work (time). The other uses O(1) auxiliary space.
    Both are single-pass algorithms, with the same asymptotic time complexity.

    >>> similar_range_alt([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0],
    ...                   4)
    range(8, 9)
    >>> similar_range_alt([5, 3, -17, 1, 4, 8, 66, 2, 9, 5, -15, 1, -1, 8, 0],
    ...                   5)
    range(9, 11)
    """
    lower = similar = 0

    for value in values:
        if value < new_value:
            lower += 1
        elif not new_value < value:
            similar += 1

    return range(lower, lower + similar)


# TODO: Name the "select by partitioning" functions--this one and the one after
#       it--after the algorithm they both implement.
def select_by_partitioning(values, k):
    """
    Recursively find the stable kth order statistic or raise IndexError.

    This finds the item at nonnegative (0-based) index k in a stable sort. Thus

        select_by_partitioning(values, k) is sorted(values)[k]

    evaluates to True when possible, and otherwise raises IndexError.

    You can assume isinstance(k, int). If k is negative, raise IndexError.

    The technique used is partition-based, calling partition3. Average time
    complexity is asymptotically optimal, but worst-case time complexity isn't.
    [FIXME: Write the best, average, and worst-case time complexities here.]

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

    lower, similar, higher = partition3(values, random.choice(values))

    if k < len(lower):
        return select_by_partitioning(lower, k)

    if k < len(lower) + len(similar):
        return similar[k - len(lower)]

    return select_by_partitioning(higher, k - (len(lower) + len(similar)))


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
        lower, similar, higher = partition3(values, random.choice(values))

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

    lower, similar, higher = partition3(values, choose_pivot(values))
    sorted_lower = _do_stable_quicksort(lower, choose_pivot)
    sorted_higher = _do_stable_quicksort(higher, choose_pivot)
    return sorted_lower + similar + sorted_higher


# TODO: Rename all three of the "sort by partitioning" functions--this one and
#       the next two below it--after the algorithm they all implement.
def sort_by_partitioning_simple(values):
    """
    Stably sort values by a partition-based technique, creating a new list.

    This does most of its work in calls to partition3. Average time complexity
    is asymptotically optimal. (What is the asymptotically optimal average-case
    time complexity for a comparison sort?) But worst-case time complexity
    isn't. [FIXME: State best, average, and worst-case time complexities here.]

    >>> sort_by_partitioning_simple([50, 90, 60, 40, 10, 80, 20, 30, 70])
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> sort_by_partitioning_simple([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0])
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]

    The average time complexity is good, but some common inputs may give
    worst-case time and/or fail with RecursionError. Ensure this doesn't happen
    for all-ascending or all-descending input. FIXME: Then enable these tests:

    >>> r1 = range(100_000)
    >>> sort_by_partitioning_simple(r1) == list(r1)  # doctest: +SKIP
    True
    >>> r2 = range(99_999, -1, -1)
    >>> sort_by_partitioning_simple(r2) == list(r1)  # doctest: +SKIP
    True
    """
    return _do_stable_quicksort(list(values), lambda seq: seq[len(seq) // 2])


def sort_by_partitioning(values):
    """
    Stably sort untrusted values by a partition-based technique, creating a new
    list.

    This is like sort_by_partitioning_simple, but naturally occurring
    combinations of sorted and reverse-sorted runs in the input are unlikely to
    cause worst-case performance or RecursionError. Also, it should be
    challenging (albeit potentially feasible) even for an expert attacker with
    full knowledge of this code and all its dependencies to craft input that
    causes degraded performance or excessive recursion depth. (Code that fails
    to do this might still pass all the currently written tests.)

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
    >>> r1 = range(100_000)
    >>> sort_by_partitioning(r1) == list(r1)
    True
    >>> r2 = range(99_999, -1, -1)
    >>> sort_by_partitioning(r2) == list(r1)
    True
    """
    return _do_stable_quicksort(list(values), random.choice)


# FIXME: This is the third of three similar implementations. Extract their
#        shared logic to a module-level nonpublic function.
def sort_by_partitioning_hardened(values):
    """
    Stably sort seriously untrusted values by a partition-based technique,
    creating a new list.

    This is like sort_by_partitioning, but it should be infeasible even for a
    team of expert attackers with full knowledge of the code and all its
    dependencies and effectively unlimited time and money to craft input that
    causes degraded performance or excessive recursion depth, except by
    exploiting a vulnerability in the platform. (Their best shot might be a
    vulnerability in the operating system or hardware.)

    The hardening measures you take must leave best, average, and worst-case
    asymptotic time complexity unchanged. However, they will introduce
    substantial constant factors, so this implementation is likely ill-suited
    to real-world use, especially considering that anyone who wants these
    benefits can just use mergesort instead, which is worst-case O(n log n).

    [FIXME: Yet this algorithm is very often preferred to mergesort! Briefly
    state, somewhere, what is different between (a) our three implementations
    of this algorithm, and (b) the way it's usually done in practice. Hint: The
    variations used in practice actually lack an often-desired feature these
    have: stability. What does lifting the stability requirement buy them?]

    >>> sort_by_partitioning_hardened([50, 90, 60, 40, 10, 80, 20, 30, 70])
    [10, 20, 30, 40, 50, 60, 70, 80, 90]
    >>> sort_by_partitioning_hardened([4.0, 1.0, 3, 2.0, True, 4, 1, 3.0])
    [1.0, True, 1, 2.0, 3, 3.0, 4.0, 4]
    >>> r1 = range(100_000)
    >>> sort_by_partitioning_hardened(r1) == list(r1)
    True
    >>> r2 = range(99_999, -1, -1)
    >>> sort_by_partitioning_hardened(r2) == list(r1)
    True
    """
    return _do_stable_quicksort(list(values), secrets.choice)


def stabilize(unstable_sort, *, materialize=False):
    """
    Create a stable sort from an unstable sort. Assume total ordering.

    This higher-order function takes any sorting function, permitted to be
    unstable, that accepts an iterable of comparable items. It returns a
    sorting function based on the given function, using conceptually almost the
    same algorithm, yet guaranteed to be stable. The output function may assume
    total ordering, but it must not reorder different objects that compare
    equal. The output function need not accept key= or reverse= arguments.

    The input function is required to be correct. The output function will then
    be correct for the same reason the input function is correct, whatever
    reason that is. Asymptotic best, average, and worst-case time complexity
    shall usually be preserved (if they are not, the input function is rather
    strange). The output function may be slower than the input function by a
    constant factor.

    The output function's asymptotic space complexity is at most that of the
    input function or O(n), whichever is greater. However, it does not perform
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
    maybe_materialize = (list if materialize else lambda x: x)

    @functools.wraps(unstable_sort)
    def stabilized_sort(values):
        augmented_input = ((x, i) for i, x in enumerate(values))
        augmented_output = unstable_sort(maybe_materialize(augmented_input))
        return [x for x, _ in augmented_output]

    return stabilized_sort


def make_deep_tuple(depth):
    """Make a tuple of the specified depth."""
    tup = ()
    for _ in range(depth):
        tup = (tup,)
    return tup


def nest(seed, degree, height):
    """
    Create a nested tuple from a seed, branching degree, and height.

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
