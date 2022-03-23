#!/usr/bin/env python

"""
Some recursion examples.

See also object_graph.py.
"""

import bisect
import collections

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
        else: # values[halfway] should = x, possibly add assert.
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
    resultlist = list(values2)
    for v1 in values1:
        bisect.insort(resultlist, v1)

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
        if values1[index1] <= values2[index2]:
            resultlist.append(values1[index1])
            index1 += 1
        else:
            resultlist.append(values2[index2])
            index2 += 1

    resultlist.extend(values1[index1:] or values2[index2:])

    return resultlist


def merge_sort(values):
    """
    Sort using merge_two recursively.

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
    >>> merge_sort([0.0, 0, False])  # Succeeds, because it's a stable sort.
    [0.0, 0, False]
    """
    def helper(values):
        # base case: length is less than 2, return the list
        if len(values) < 2:
            return values

        halfway = len(values) // 2
        return merge_two(helper(values[:halfway]), helper(values[halfway:]))

    return helper(list(values))


def merge_sort_bottom_up_unstable(values):
    """
    Sort bottom-up, using merge_two, iteratively. Unstable.

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
        queue.append(merge_two(left, right))

    return queue[0]


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


def flatten(root):
    """
    Using recursion, lazily flatten a tuple, yielding all leaves (non-tuples).

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
