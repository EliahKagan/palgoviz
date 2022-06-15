#!/usr/bin/env python

"""
Some recursion examples (and a few related iterative implementations).

See also object_graph.py.
"""

import bisect
import collections

import decorators


def countdown(n):
    """
    Recursively count down from n, printing the positive numbers, one per line.

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
    Add all the numbers iteratively. Like sum(values).

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
    Find an index to some occurrence of x in values, if any, in a Pythonic way.

    If there are no occurrences of x in values, None is returned.

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
    Iteratively find an index to some occurrence of x in values, if any.

    If there are no occurrences of x in values, None is returned.

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


def linear_search_iterative_alt(values, x):
    """
    Iteratively find an index to some occurrence of x in values, if any.

    If there are no occurrences of x in values, None is returned.

    This is an alternative implementation of linear_search_iterative (above).
    One implementation uses no comprehensions; the other uses no loops.

    >>> linear_search_iterative_alt([], 9)
    >>> linear_search_iterative_alt([2, 3], 2)
    0
    >>> linear_search_iterative_alt((4, 5, 6), 5)
    1
    >>> linear_search_iterative_alt([3, 1, 2, 8, 6, 5, 7], 8)
    3
    """
    matches = (index for index, value in enumerate(values) if value == x)
    return next(matches, None)


def linear_search(values, x):
    """
    Recursively find an index to some occurrence of x in values, if any.

    If there are no occurrences of x in values, None is returned.

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
    Recursively find an index to an occurrence of x in values, which is sorted.

    If there are no occurrences of x in values, None is returned.

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
    Iteratively find an index to an occurrence of x in values, which is sorted.

    If there are no occurrences of x in values, None is returned.

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


def binary_search_alt(values, x):
    """
    Recursively find an index to an occurrence of x in values, which is sorted.

    If there are no occurrences of x in values, None is returned.

    This alternative implementation of binary_search uses high as an exclusive,
    rather than inclusive, endpoint. This is an implementation detail and does
    not affect externally observable behavior.

    >>> binary_search_alt([], 9)
    >>> binary_search_alt([2, 3], 2)
    0
    >>> binary_search_alt((4, 5, 6), 5)
    1
    >>> binary_search_alt((4, 5, 6), 7)
    >>> binary_search_alt([1, 2, 3, 5, 6, 7, 8], 3)
    2
    >>> binary_search_alt([10], 10)
    0
    >>> binary_search_alt([10, 20], 10)
    0
    >>> binary_search_alt([10, 20], 20)
    1
    >>> binary_search_alt([10, 20], 15)
    >>>
    """
    def search(low, high):
        if high <= low:
            return None
        mid = (low + high) // 2
        if values[mid] < x:
            return search(mid + 1, high)
        if values[mid] > x:
            return search(low, mid)
        return mid

    return search(0, len(values))


def binary_search_iterative_alt(values, x):
    """
    Iteratively find an index to an occurrence of x in values, which is sorted.

    If there are no occurrences of x in values, None is returned.

    This alternative implementation of binary_search_iterative uses high as an
    exclusive, rather than inclusive, endpoint. This is an implementation
    detail and does not affect externally observable behavior.

    >>> binary_search_iterative_alt([], 9)
    >>> binary_search_iterative_alt([2, 3], 2)
    0
    >>> binary_search_iterative_alt((4, 5, 6), 5)
    1
    >>> binary_search_iterative_alt((4, 5, 6), 7)
    >>> binary_search_iterative_alt([1, 2, 3, 5, 6, 7, 8], 3)
    2
    >>> binary_search_iterative_alt([10], 10)
    0
    >>> binary_search_iterative_alt([10, 20], 10)
    0
    >>> binary_search_iterative_alt([10, 20], 20)
    1
    >>> binary_search_iterative_alt([10, 20], 15)
    >>>
    """
    low = 0
    high = len(values)

    while low < high:
        mid = (low + high) // 2
        if values[mid] < x:
            low = mid + 1
        elif values[mid] > x:
            high = mid
        else:
            return mid

    return None


def binary_search_good(values, x):
    """
    Find an index to an occurrence of x in values, which is sorted.

    If there is no such occurrence, None is returned.

    This implementation uses a function in the bisect module.

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
