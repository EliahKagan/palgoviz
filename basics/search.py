"""
Searching.

See also recursion.py.
"""

import bisect
import operator


def _identity_function(arg):
    """Identity function. Return the argument unchanged."""
    return arg


def bsearch(values, x, key=None, reverse=False):
    """
    Binary search.

    Find the index of some y in values where neither x nor key(y) is lesser.
    Assume values is sorted as if by values.sort(key=key, reverse=reverse), but
    it may be of any sequence type (it need not be a list). If key is None or
    not passed, y is its own key: look for a y where neither x nor y is lesser.

    Time complexity is O(log n). Auxiliary space complexity is O(1). This
    implementation may be similar to one of your binary search implementations
    in recursion.py, but this supports an optional key selector, allows
    reverse-sorted input, and raises ValueError if the search finds no result.

    NOTE: I highly recommend NOT LOOKING at the binary search implementations
    in recursion.py (and not even their names and descriptions) while working
    this exercise. Usually it is very good to look at what you've already done,
    but I think this exercise will be much, MUCH more beneficial if you do not.

    [FIXME: After you are satisfied this solution is correct and all tests
    pass, review all your binary search implementations in recursion.py and
    replace this with a statement of which one this is similar to, if any. Also
    state, for each approach there that you didn't use here, if you could've
    used it here, why or why not, and, for any you could've used, any major
    advantages or disadvantages they would have, compared to what you did use.
    If an approach would require considerably more code, you should still
    consider it feasible... *if* you are convinced that it really can be done.]
    """
    if key is None:
        key = _identity_function
    compare = operator.gt if reverse else operator.lt

    low = 0
    high = len(values)

    while low < high:
        mid = (low + high) // 2
        mapped_key = key(values[mid])

        if compare(x, mapped_key):
            high = mid  # Go left.
        elif compare(mapped_key, x):
            low = mid + 1  # Go right.
        else:
            return mid

    raise ValueError(f'no item found with key similar to {x!r}')


def _ensure_not_reverse_comparing_instance(other):
    """Helper to make comparing two _ReverseComparing objects a hard error."""
    if isinstance(other, _ReverseComparing):
        raise TypeError('tried to compare two _ReverseComparing instances')


class _ReverseComparing:
    """
    Wrapper that holds an item, with reversed strict-order comparisons.

    This is an implementation detail of bsearch_alt. Other types should not try
    to implement "<", ">", "<=", or ">=" comparisons with _ReverseComparing.
    """

    __slots__ = ('item',)

    def __init__(self, item):
        self.item = item

    def __repr__(self):
        return f'{type(self).__name__}({self.item!r})'

    def __lt__(self, other):
        _ensure_not_reverse_comparing_instance(other)
        return other < self.item

    def __gt__(self, other):
        _ensure_not_reverse_comparing_instance(other)
        return other > self.item


def bsearch_alt(values, x, key=None, reverse=False):
    """
    Binary search, [FIXME: very briefly state how this function is different].

    This alternative implementation of bsearch must use a different technique.
    It has the same requirements, including restrictions on time and space. It
    should use the same approach as in one of the functions in recursion.py
    (but not the one, if any, whose approach bsearch uses above), unless that's
    not possible, as detailed in the text you added to the bsearch docstring.
    """
    if key is None:
        key = _identity_function

    x_for_bisect = (_ReverseComparing(x) if reverse else x)
    index = bisect.bisect_left(values, x_for_bisect, key=key)

    if index == len(values) or x_for_bisect < key(values[index]):
        raise ValueError(f'no item found with key similar to {x!r}')

    return index


def two_sum_slow(numbers, total):
    """
    Find indices of two numbers that sum to total. Minimize auxiliary space.

    Although the numbers may be equal, the indices must be unequal. Give the
    left index before the right one. If there are multiple solutions, return
    any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    # Although un-Pythonic, this code avoids obscuring how the algorithm works.
    for left in range(len(numbers)):
        for right in range(left + 1, len(numbers)):
            if numbers[left] + numbers[right] == total:
                return left, right

    raise ValueError(f'no two numbers sum to {total!r}')


def two_sum_fast(numbers, total):
    """
    Find indices of two numbers that sum to total. Minimize running time.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    history = {}

    for right, value in enumerate(numbers):
        try:
            left = history[total - value]
        except KeyError:
            history[right] = value
        else:
            return left, right

    raise ValueError(f'no two numbers sum to {total!r}')


def _two_sum_sorted_keyed(items, total, key):
    """Solve sorted 2-sum problem where map(key, items) are the numbers."""
    left = 0
    right = len(items) - 1

    while left < right:
        total_here = key(items[left]) + key(items[right])
        if total_here < total:
            left += 1
        elif total_here > total:
            right -= 1
        else:
            return left, right

    raise ValueError(f'no two numbers sum to {total!r}')


def two_sum_sorted(numbers, total):
    """
    Given sorted numbers, find indices of two numbers that sum to total.

    Minimize both running time and auxiliary space, to the extent possible.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here. If
    they are independently optimal, meaning this problem cannot be solved in
    asymptotically less time even with unlimited space, nor in asymptotically
    less space even in unlimited time, then say so and explain why. Otherwise,
    say why that cannot be done, and explain why you believe the tradeoff you
    picked between time and space is a reasonable choice.]
    """
    return _two_sum_sorted_keyed(numbers, total, lambda num: num)


def two_sum_nohash(numbers, total):
    """
    Find indices of two numbers that sum to total, without hashing.

    Minimize running time. If this and a previous function have substantial
    overlapping logic, extract it a nonpublic module-level function.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    indices = sorted(range(len(numbers)), key=numbers.__getitem__)
    left, right = _two_sum_sorted_keyed(indices, total, numbers.__getitem__)
    return indices[left], indices[right]
