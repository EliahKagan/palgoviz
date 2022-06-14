#!/usr/bin/env python

"""
Searching.

See also recursion.py.

It is often said, including in the Python documentation and in this module's
docstrings, that a sequence must be sorted for binary search to work correctly.
But the actual precondition is much weaker: [TODO: After doing the relevant
exercises in this module, replace this bracketed text with a statement of the
weaker precondition and a list of all functions it applies to in this module.]
"""

import bisect
import functools
import math
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

    Time complexity is the usual [FIXME: give it, in big-O]. Auxiliary space
    complexity is O(1). This implementation may be similar to one of your
    binary search implementations in recursion.py, but this supports an
    optional key selector, allows reverse-sorted input, and raises ValueError
    if the search finds no result.

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

    >>> bsearch(range(99, -1, -1), 17, reverse=True)
    82
    >>> bsearch(range(100), 289, key=lambda x: x**2)
    17
    >>> bsearch(range(99, -1, -1), 289, key=lambda x: x**2, reverse=True)
    82
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> bsearch(words, 4, key=len, reverse=True)
    1
    >>> bsearch(words, 3, key=len, reverse=True) in (2, 3, 4)
    True
    >>> bsearch(words, 5, key=len, reverse=True)
    Traceback (most recent call last):
      ...
    ValueError: no item found with key similar to 5
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

    >>> bsearch_alt(range(99, -1, -1), 17, reverse=True)
    82
    >>> bsearch_alt(range(100), 289, key=lambda x: x**2)
    17
    >>> bsearch_alt(range(99, -1, -1), 289, key=lambda x: x**2, reverse=True)
    82
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> bsearch_alt(words, 4, key=len, reverse=True)
    1
    >>> bsearch_alt(words, 3, key=len, reverse=True) in (2, 3, 4)
    True
    >>> bsearch_alt(words, 5, key=len, reverse=True)
    Traceback (most recent call last):
      ...
    ValueError: no item found with key similar to 5
    """
    if key is None:
        key = _identity_function

    x_for_bisect = (_ReverseComparing(x) if reverse else x)
    index = bisect.bisect_left(values, x_for_bisect, key=key)

    if index == len(values) or x_for_bisect < key(values[index]):
        raise ValueError(f'no item found with key similar to {x!r}')

    return index


def first_satisfying_recursive(predicate, low, high):
    """
    Find the first int satisfying a predicate that partitions the search space.

    The caller must ensure that there is some int k where low <= k <= high and:

      - For every int i where low <= i < k, predicate(i) is falsy.
      - For every int j where k <= j < high, predicate(j) is truthy.

    That is, within the given bounds, if an argument is high enough to satisfy
    the predicate, increasing it continues to satisfy the predicate. This finds
    the lowest value high enough to satisfy the predicate (which is what k is).

    It follows that (a) if the predicate is never satisfied, high is returned,
    and (b) the caller ensures low <= high. (Make sure you understand why.) But
    as an additional feature, allow high < low. Return high when that happens.

    This implementation is recursive. It may use builtins, but no other library
    facilities. Its time complexity is asymptotically optimal. [FIXME: State
    the asymptotic time and auxiliary space complexities, if predicate calls
    take O(1) time and space. Explain why no asymptotically faster algorithm
    for this problem is possible, no matter what techniques are used.]

    >>> first_satisfying_recursive(lambda _: False, -8, 9)
    9
    >>> first_satisfying_recursive(lambda _: print("Shouldn't print!"), 3, 3)
    3
    >>> first_satisfying_recursive(lambda _: print("Shouldn't print!"), 8, 4)
    4
    >>> first_satisfying_recursive(lambda x: x**2 >= 31329, 0, 500)
    177
    >>> y = 507462686636302216327655657023048145390646150  # y = x**3 - x**2
    >>> first_satisfying_recursive(lambda x: x**3 - x**2 >= y, 0, y + 1)
    797629800584935
    """
    if low >= high:
        return high
    mid = (low + high) // 2
    if predicate(mid):
        return first_satisfying_recursive(predicate, low, mid)
    return first_satisfying_recursive(predicate, mid + 1, high)


def first_satisfying(predicate, low, high):
    """
    Find the first int satisfying a predicate that partitions the search space.

    This is like first_satisfying_recursive but iterative instead of recursive.
    It also may use builtins but no other library facilities. The algorithm is
    the same as, or very similar to, that algorithm.

    This has the same asymptotic time complexity as first_satisfying. Its
    auxiliary space complexity is [FIXME: state it asymptotically here].

    >>> first_satisfying(lambda _: False, -8, 9)
    9
    >>> first_satisfying(lambda _: print("Shouldn't print!"), 3, 3)
    3
    >>> first_satisfying(lambda _: print("Shouldn't print!"), 8, 4)
    4
    >>> first_satisfying(lambda x: x**2 >= 31329, 0, 500)
    177
    >>> y = 507462686636302216327655657023048145390646150  # y = x**3 - x**2
    >>> first_satisfying(lambda x: x**3 - x**2 >= y, 0, y + 1)
    797629800584935
    """
    while low < high:
        mid = (low + high) // 2
        if predicate(mid):
            high = mid
        else:
            low = mid + 1

    return high


# !!FIXME: When removing implementation bodies, remove "=bisect.bisect_left".
def first_satisfying_restricted(predicate, low, high, *,
                                bisector=bisect.bisect_left):
    """
    Use the bisect module to find the first int satisfying a predicate that
    partitions the search space.

    This is like first_satisfying_recursive and first_satisfying, but worse:
    the search space must be small enough for its size to be expressed in a
    native word (specifically, the ssize_t type). Unlike previous versions,
    this is permitted to use more than builtins, and must do so: all but O(1)
    of its work must happen behind a call to something in the bisect module.

    Whatever function in the bisect module you use, accept it by dependency
    injection via the keyword-only bisector argument. That way, if you later
    write an unrestricted version of that function, you'll be able to test that
    the test case raising OverflowError below succeeds if it is passed instead.
    (If you decide the name "bisector" is ambiguous or misleading, rename it.)

    This has the same asymptotic time complexity as first_satisfying_recursive
    and first_satisfying. Its auxiliary space complexity is [FIXME: state it].

    [FIXME: State what operation triggers the OverflowError. It depends on how
    you implement this. There are two possibilities, yet there isn't really a
    reasonable way to avoid the error (besides using your own "bisector"). Once
    you have the behavior you think you want, remove the "ELLIPSIS" doctest
    option and replace "..." in "OverflowError: ..." with an expected message.]

    >>> first_satisfying_restricted(lambda _: False, -8, 9)
    9
    >>> first_satisfying_restricted(lambda _: print("Shouldn't print!"), 3, 3)
    3
    >>> first_satisfying_restricted(lambda _: print("Shouldn't print!"), 8, 4)
    4
    >>> first_satisfying_restricted(lambda x: x**2 >= 31329, 0, 500)
    177
    >>> y = 507462686636302216327655657023048145390646150  # y = x**3 - x**2
    >>> first_satisfying_restricted(lambda x: x**3 - x**2 >= y, 0, y + 1)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    OverflowError: ...
    """
    if high < low:
        return high
    delta = high - low
    return low + bisector(range(low, high), 1, lo=0, hi=delta, key=predicate)


def my_bisect_left(values, x, lo=0, hi=None, *, key=None, reverse=False):
    """
    Find the leftmost insertion point for a new key x in a sorted sequence.

    This is like bisect.bisect_left, except reverse-sorted input is supported
    (when reverse=True). Since it can be useful to pass lo and hi as keyword
    arguments, their names are retained for compatibility (instead of following
    the conventions elsewhere in this project and calling them low and high).

    As in bisect.bisect_left, the key function is applied to elements of values
    but not to x, and if key is not passed, every element is its own key.
    Assume values is sorted as if by values.sort(key=key, reverse=reverse).

    This doesn't use the bisect module. It does use some function defined above
    this point in this module, which doesn't use the bisect module either, not
    even indirectly. All but O(1) work happens behind a call to that function.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> mixed = [None, None, 2, 2, -3, 3, -3, 8, -19, 19, -44, -45, None, None]
    >>> my_bisect_left(mixed, 3, lo=2, hi=12, key=abs)
    4
    >>> my_bisect_left(mixed, 50, lo=2, hi=12, key=abs)
    12
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> my_bisect_left(words, 4, key=len, reverse=True)
    1
    >>> my_bisect_left(words, 3, key=len, reverse=True)
    2
    >>> my_bisect_left(words, 5, key=len, reverse=True)
    1
    """
    if hi is None:
        hi = len(values)
    if key is None:
        key = _identity_function
    strict_compare = operator.gt if reverse else operator.lt

    def non_strict_compare(lhs, rhs):
        return not strict_compare(rhs, lhs)  # rhs doesn't have to come first.

    def predicate(index):
        return non_strict_compare(x, key(values[index]))  # x ≾ y

    return first_satisfying(predicate, lo, hi)


def my_bisect_right(values, x, lo=0, hi=None, *, key=None, reverse=False):
    """
    Find the rightmost insertion point for a new key x in a sorted sequence.

    This is analogous to my_bisect_left, but for bisect.bisect_right. It has
    the same preconditions including how values comes sorted, and likewise must
    not use the bisect module but must do all but O(1) of its work behind some
    above-defined function (that doesn't either). Do not use my_bisect_left.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> mixed = [None, None, 2, 2, -3, 3, -3, 8, -19, 19, -44, -45, None, None]
    >>> my_bisect_right(mixed, 3, lo=2, hi=12, key=abs)
    7
    >>> my_bisect_right(mixed, 50, lo=2, hi=12, key=abs)
    12
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> my_bisect_right(words, 4, key=len, reverse=True)
    2
    >>> my_bisect_right(words, 3, key=len, reverse=True)
    5
    >>> my_bisect_right(words, 5, key=len, reverse=True)
    1
    """
    if hi is None:
        hi = len(values)
    if key is None:
        key = _identity_function
    strict_compare = operator.gt if reverse else operator.lt

    def predicate(index):
        return strict_compare(x, key(values[index]))  # x < y

    return first_satisfying(predicate, lo, hi)


def my_bisect_left_recursive_simple(values, x):
    """
    Find the leftmost insertion point for x in sorted values (total ordering).

    This is a recursive limited version of bisect.bisect_left: the elements of
    values may be assumed to support all six rich comparison operators with
    total ordering semantics, and lo, hi, and key arguments are not accepted.

    This variation of classic recursive binary search finds the furthest left
    insertion point rather than a matching element. Its code is self-contained
    except for builtins and its own helpers (if any). Don't reimplement the
    function that my_bisect_left and my_bisect_right use to do their work.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    my_bisect_left_recursive (below) is like this but more complicated.

    >>> a = (20, 20, 20, 40, 40, 60, 70, 70, 70, 100)
    >>> {x: my_bisect_left_recursive_simple(a, x) for x in range(10, 101, 10)}
    {10: 0, 20: 0, 30: 3, 40: 3, 50: 5, 60: 5, 70: 6, 80: 9, 90: 9, 100: 9}

    >>> class S(str):
    ...     def __repr__(self):
    ...         return f'{type(self).__name__}({super().__repr__()})'
    >>> b = []
    >>> for x in 'ham', 'foo', 'bar', 'baz', 'quux', S('ham'), 'spam', 'eggs':
    ...     b.insert(my_bisect_left_recursive_simple(b, x), x)
    >>> b
    ['bar', 'baz', 'eggs', 'foo', S('ham'), 'ham', 'quux', 'spam']
    """
    def search(low, high):
        if low >= high:
            return high
        mid = (low + high) // 2
        if values[mid] < x:
            return search(mid + 1, high)
        return search(low, mid)

    return search(0, len(values))


def my_bisect_left_iterative_simple(values, x):
    """
    Find the leftmost insertion point for x in sorted values (total ordering).

    This is a nonrecursive limited version of bisect.bisect_left: the elements
    of values may be assumed to support all six rich comparison operators with
    total ordering semantics, and lo, hi, and key arguments are not accepted.

    This variation of classic iterative binary search finds the furthest left
    insertion point rather than a matching element. Its code is self-contained
    except for builtins and its own helpers (if any). Don't reimplement the
    function that my_bisect_left and my_bisect_right use to do their work.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    my_bisect_left_iterative (below) is like this but more complicated.

    >>> a = (20, 20, 20, 40, 40, 60, 70, 70, 70, 100)
    >>> {x: my_bisect_left_iterative_simple(a, x) for x in range(10, 101, 10)}
    {10: 0, 20: 0, 30: 3, 40: 3, 50: 5, 60: 5, 70: 6, 80: 9, 90: 9, 100: 9}

    >>> class S(str):
    ...     def __repr__(self):
    ...         return f'{type(self).__name__}({super().__repr__()})'
    >>> b = []
    >>> for x in 'ham', 'foo', 'bar', 'baz', 'quux', S('ham'), 'spam', 'eggs':
    ...     b.insert(my_bisect_left_iterative_simple(b, x), x)
    >>> b
    ['bar', 'baz', 'eggs', 'foo', S('ham'), 'ham', 'quux', 'spam']
    """
    low = 0
    high = len(values)

    while low < high:
        mid = (low + high) // 2
        if values[mid] < x:
            low = mid + 1
        else:
            high = mid

    return high


def my_bisect_right_recursive_simple(values, x):
    """
    Find the rightmost insertion point for x in sorted values (total ordering).

    This is a recursive limited version of bisect.bisect_right: the elements
    of values may be assumed to support all six rich comparison operators with
    total ordering semantics, and lo, hi, and key arguments are not accepted.

    This variation of classic recursive binary search finds the furthest right
    insertion point rather than a matching element. Its code is self-contained
    except for builtins and its own helpers (if any). Don't reimplement the
    function that my_bisect_left and my_bisect_right use to do their work.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    my_bisect_right_recursive (below) is like this but more complicated.

    >>> a = (20, 20, 20, 40, 40, 60, 70, 70, 70, 100)
    >>> {x: my_bisect_right_recursive_simple(a, x) for x in range(10, 101, 10)}
    {10: 0, 20: 3, 30: 3, 40: 5, 50: 5, 60: 6, 70: 9, 80: 9, 90: 9, 100: 10}

    >>> class S(str):
    ...     def __repr__(self):
    ...         return f'{type(self).__name__}({super().__repr__()})'
    >>> b = []
    >>> for x in 'ham', 'foo', 'bar', 'baz', 'quux', S('ham'), 'spam', 'eggs':
    ...     b.insert(my_bisect_right_recursive_simple(b, x), x)
    >>> b
    ['bar', 'baz', 'eggs', 'foo', 'ham', S('ham'), 'quux', 'spam']
    """
    def search(low, high):
        if low >= high:
            return high
        mid = (low + high) // 2
        if values[mid] <= x:
            return search(mid + 1, high)
        return search(low, mid)

    return search(0, len(values))


def my_bisect_right_iterative_simple(values, x):
    """
    Find the rightmost insertion point for x in sorted values (total ordering).

    This is a nonrecursive limited version of bisect.bisect_right: the elements
    of values may be assumed to support all six rich comparison operators with
    total ordering semantics, and lo, hi, and key arguments are not accepted.

    This variation of classic iterative binary search finds the furthest right
    insertion point rather than a matching element. Its code is self-contained
    except for builtins and its own helpers (if any). Don't reimplement the
    function that my_bisect_left and my_bisect_right use to do their work.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    my_bisect_right_iterative (below) is like this but more complicated.

    >>> a = (20, 20, 20, 40, 40, 60, 70, 70, 70, 100)
    >>> {x: my_bisect_right_iterative_simple(a, x) for x in range(10, 101, 10)}
    {10: 0, 20: 3, 30: 3, 40: 5, 50: 5, 60: 6, 70: 9, 80: 9, 90: 9, 100: 10}

    >>> class S(str):
    ...     def __repr__(self):
    ...         return f'{type(self).__name__}({super().__repr__()})'
    >>> b = []
    >>> for x in 'ham', 'foo', 'bar', 'baz', 'quux', S('ham'), 'spam', 'eggs':
    ...     b.insert(my_bisect_right_iterative_simple(b, x), x)
    >>> b
    ['bar', 'baz', 'eggs', 'foo', 'ham', S('ham'), 'quux', 'spam']
    """
    low = 0
    high = len(values)

    while low < high:
        mid = (low + high) // 2
        if values[mid] <= x:
            low = mid + 1
        else:
            high = mid

    return high


def _do_bisect_left(values, x, low, high, key, compare):
    """Recursive helper function for my_bisect_left_recursive."""
    if high <= low:
        return high
    mid = (low + high) // 2
    if compare(key(values[mid]), x):  # y < x
        return _do_bisect_left(values, x, mid + 1, high, key, compare)
    return _do_bisect_left(values, x, low, mid, key, compare)


def my_bisect_left_recursive(values, x, lo=0, hi=None, *,
                             key=None, reverse=False):
    """
    Find the leftmost insertion point for a new key x in a sorted sequence.

    This recursive alternative implementation of my_bisect_left does not use
    anything from the bisect module, nor anything else in this module, except
    that its helpers (if any) may be top-level functions. Don't reimplement the
    function that my_bisect_left and my_bisect_right use to do their work.

    This should be a classic recursive binary search implementation, but to
    find the furthest left insertion point rather than a matching element, and
    supporting key and reverse. So this code differs from my_bisect_left, even
    though both implement bisect.bisect_left (and both add "reverse" support).

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> mixed = [None, None, 2, 2, -3, 3, -3, 8, -19, 19, -44, -45, None, None]
    >>> my_bisect_left_recursive(mixed, 3, lo=2, hi=12, key=abs)
    4
    >>> my_bisect_left_recursive(mixed, 50, lo=2, hi=12, key=abs)
    12
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> my_bisect_left_recursive(words, 4, key=len, reverse=True)
    1
    >>> my_bisect_left_recursive(words, 3, key=len, reverse=True)
    2
    >>> my_bisect_left_recursive(words, 5, key=len, reverse=True)
    1

    [FIXME: If you used bisect.bisect_left in first_satisfying_restricted,
    replace this with a doctest showing that injecting my_bisect_left_recursive
    as the dependency avoids OverflowError. Otherwise, just remove this.]

    !!FIXME: When removing implementation bodies, remove this doctest:

    >>> y = 507462686636302216327655657023048145390646150  # y = x**3 - x**2
    >>> first_satisfying_restricted(lambda x: x**3 - x**2 >= y, 0, y + 1,
    ...                             bisector=my_bisect_left_recursive)
    797629800584935
    """
    if hi is None:
        hi = len(values)
    if key is None:
        key = _identity_function
    compare = operator.gt if reverse else operator.lt
    return _do_bisect_left(values, x, lo, hi, key, compare)


def my_bisect_left_iterative(values, x, lo=0, hi=None, *,
                             key=None, reverse=False):
    """
    Find the leftmost insertion point for a new key x in a sorted sequence.

    This nonrecursive alternative implementation of my_bisect_left is like
    my_bisect_left_recursive, but iterative instead of recursive.

    This should be a classic iterative binary search implementation, but to
    find the furthest left insertion point rather than a matching element, and
    supporting key and reverse. So this code differs from my_bisect_left, even
    though both implement bisect.bisect_left (and both add "reverse" support).

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> mixed = [None, None, 2, 2, -3, 3, -3, 8, -19, 19, -44, -45, None, None]
    >>> my_bisect_left_iterative(mixed, 3, lo=2, hi=12, key=abs)
    4
    >>> my_bisect_left_iterative(mixed, 50, lo=2, hi=12, key=abs)
    12
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> my_bisect_left_iterative(words, 4, key=len, reverse=True)
    1
    >>> my_bisect_left_iterative(words, 3, key=len, reverse=True)
    2
    >>> my_bisect_left_iterative(words, 5, key=len, reverse=True)
    1

    [FIXME: If you used bisect.bisect_left in first_satisfying_restricted,
    replace this with a doctest showing that injecting my_bisect_left_iterative
    as the dependency avoids OverflowError. Otherwise, just remove this.]

    !!FIXME: When removing implementation bodies, remove this doctest:

    >>> y = 507462686636302216327655657023048145390646150  # y = x**3 - x**2
    >>> first_satisfying_restricted(lambda x: x**3 - x**2 >= y, 0, y + 1,
    ...                             bisector=my_bisect_left_iterative)
    797629800584935
    """
    if hi is None:
        hi = len(values)
    if key is None:
        key = _identity_function
    compare = operator.gt if reverse else operator.lt

    while lo < hi:
        mid = (lo + hi) // 2
        if compare(key(values[mid]), x):  # y < x
            lo = mid + 1
        else:
            hi = mid

    return hi


def _do_bisect_right(values, x, low, high, key, compare):
    """Recursive helper function for my_bisect_right_recursive."""
    if high <= low:
        return high
    mid = (low + high) // 2
    if compare(x, key(values[mid])):  # x < y
        return _do_bisect_right(values, x, low, mid, key, compare)
    return _do_bisect_right(values, x, mid + 1, high, key, compare)


def my_bisect_right_recursive(values, x, lo=0, hi=None, *,
                              key=None, reverse=False):
    """
    Find the rightmost insertion point for a new key x in a sorted sequence.

    This recursive alternative implementation of my_bisect_right is like
    my_bisect_left_recursive, but it is a right rather than a left bisection.

    This should be a classic recursive binary search implementation, but to
    find the furthest right insertion point rather than a matching element, and
    supporting key and reverse. So this code differs from my_bisect_right, even
    though both implement bisect.bisect_right (and both add "reverse" support).

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> mixed = [None, None, 2, 2, -3, 3, -3, 8, -19, 19, -44, -45, None, None]
    >>> my_bisect_right_recursive(mixed, 3, lo=2, hi=12, key=abs)
    7
    >>> my_bisect_right_recursive(mixed, 50, lo=2, hi=12, key=abs)
    12
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> my_bisect_right_recursive(words, 4, key=len, reverse=True)
    2
    >>> my_bisect_right_recursive(words, 3, key=len, reverse=True)
    5
    >>> my_bisect_right_recursive(words, 5, key=len, reverse=True)
    1

    [FIXME: If you used bisect.bisect_right (also called bisect.bisect) in
    first_satisfying_restricted, replace this with a doctest showing that
    injecting my_bisect_right_recursive as the dependency avoids OverflowError.
    Otherwise, just remove this.]
    """
    if hi is None:
        hi = len(values)
    if key is None:
        key = _identity_function
    compare = operator.gt if reverse else operator.lt
    return _do_bisect_right(values, x, lo, hi, key, compare)


def my_bisect_right_iterative(values, x, lo=0, hi=None, *,
                              key=None, reverse=False):
    """
    Find the rightmost insertion point for a new key x in a sorted sequence.

    This nonrecursive alternative implementation of my_bisect_right is like
    my_bisect_right_recursive, but iterative instead of recursive. So it's like
    my_bisect_left_iterative, but it is a right rather than a left bisection.

    This should be a classic iterative binary search implementation, but to
    find the furthest right insertion point rather than a matching element, and
    supporting key and reverse. So this code differs from my_bisect_right, even
    though both implement bisect.bisect_right (and both add "reverse" support).

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> mixed = [None, None, 2, 2, -3, 3, -3, 8, -19, 19, -44, -45, None, None]
    >>> my_bisect_right_iterative(mixed, 3, lo=2, hi=12, key=abs)
    7
    >>> my_bisect_right_iterative(mixed, 50, lo=2, hi=12, key=abs)
    12
    >>> words = ['foobar', 'quux', 'baz', 'bar', 'foo']
    >>> my_bisect_right_iterative(words, 4, key=len, reverse=True)
    2
    >>> my_bisect_right_iterative(words, 3, key=len, reverse=True)
    5
    >>> my_bisect_right_iterative(words, 5, key=len, reverse=True)
    1

    [FIXME: If you used bisect.bisect_right (also called bisect.bisect) in
    first_satisfying_restricted, replace this with a doctest showing that
    injecting my_bisect_right_iterative as the dependency avoids OverflowError.
    Otherwise, just remove this.]
    """
    if hi is None:
        hi = len(values)
    if key is None:
        key = _identity_function
    compare = operator.gt if reverse else operator.lt

    while lo < hi:
        mid = (lo + hi) // 2
        if compare(x, key(values[mid])):  # x < y
            hi = mid
        else:
            lo = mid + 1

    return hi


# FIXME: (A) If the function first_satisfying_restricted used from the bisect
# module was neither bisect.bisect_left nor bisect.bisect_right/bisect.bisect,
# then reimplement that function here (without the ssize_t restriction). You
# can call other functions in this module, but not any of the first_satisfying
# functions, nor anything that directly or indirectly calls them. Write a few
# tests (of any kind) of your new function, at least one of which must show
# that injecting it as first_satisfying_restricted's bisector dependency avoids
# OverflowError. (B) But if it was one of those, just remove this comment.

# NOTE: Having done all the above exercises, do the module docstring TODO.


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


def has_subset_sum_slow(numbers, total):
    """
    Check if any zero or more values in numbers sum to total.

    This is the subset sum decision problem. The name is misleading, as really
    the input represents a multiset (a.k.a. bag). The problem is to determine
    if any submultiset sums to the target total. So if a value appears k times
    in numbers, it may appear up to k times in a sum. All values are integers.

    This is a decision problem, so just return True or False. Algorithms that
    solve this can be adapted to solve the more useful problem of building and
    returning some "subset" that sums to the target, when there is one. Future
    exercises may cover that, together with more techniques for both versions.

    Although the input represents a multiset (so order doesn't matter), it is
    usually supplied as a sequence, and numbers is guaranteed to be a sequence
    here. You can, and probably should, rely on that in your solution.

    This implementation is recursive. It takes exponential time. It should
    sacrifice speed for simplicity, except that I do recommend avoiding
    unnecessary copying, in which case it will take O(2**len(numbers)) time.
    """
    def check(start, subtotal):
        if subtotal == 0:
            return True
        if start == len(numbers):
            return False
        return (check(start + 1, subtotal - numbers[start]) or
                check(start + 1, subtotal))

    return check(0, total)


def has_subset_sum(numbers, total):
    """
    Efficiently check if any zero or more values in numbers sum to total.

    This is the subset sum decision problem described in has_subset_sum_slow.
    This implementation is also recursive, resembling the implementation there,
    but much more efficient. This is fast enough for substantial problem sizes.

    [FIXME: Say something about this algorithm's asymptotic time complexity.]
    """
    memo = {}

    def check(start, subtotal):
        if subtotal == 0:
            return True
        if start == len(numbers):
            return False

        try:
            return memo[start, subtotal]
        except KeyError:
            result = memo[start, subtotal] = (
                check(start + 1, subtotal - numbers[start]) or
                check(start + 1, subtotal)
            )
            return result

    return check(0, total)


def has_subset_sum_alt(numbers, total):
    """
    Efficiently check if any zero or more values in numbers sum to total.

    This alternative implementation of has_subset_sum uses the same recursive
    algorithm (so it has the same asymptotic time complexity), but implements
    it using a substantially different technique. One implementation uses a
    previously created facility in another module of this project, or a similar
    facility in the standard library. The other does not use any such facility.

    FIXME: Unlike the standard library facility, the one in this project is
    cumbersome to use for problems like subset sum, due to a limitation that
    wasn't relevant in prior uses. Rename the existing version descriptively.
    Write a new version, appropriately generalized, that overcomes that
    limitation. (Give it the name your original implementation previously had.)
    """
    @functools.cache
    def check(start, subtotal):
        if subtotal == 0:
            return True
        if start == len(numbers):
            return False
        return (check(start + 1, subtotal - numbers[start]) or
                check(start + 1, subtotal))

    return check(0, total)


def count_coin_change_slow(coins, total):
    """
    Count how many ways to make change for a total with the coins.

    coins is a sequence of positive integer coin denominations, and total is a
    a positive integer amount for which change is to be made. All coins are
    available in unlimited quantities. A way to make change is a multiset of
    coins, so ways differing only in the order of the coins are the same way.
    So (5, 2, 2) and (2, 5, 2) are the same way to make change for 10, but they
    differ from (6, 1, 3).

    But if the same value appears more than once in coins, they are distinct
    coin types happening to have the same value. So in a currency with a 1¢
    piece, a 2¢ piece portraying the king, and a 2¢ piece portraying the queen:

    >>> count_coin_change_slow([1, 2, 2], 5)
    6

    This implementation is recursive. It takes exponential time, sacrificing
    speed for simplicity other than avoiding unnecessary copying. It may
    resemble the solution to has_subset_sum_slow in other ways, too.
    """
    def count(start, subtotal):
        if subtotal == 0:
            return 1
        if start == len(coins):
            return 0
        return sum(count(start + 1, next_subtotal)
                   for next_subtotal in range(subtotal, -1, -coins[start]))

    return count(0, total)


def count_coin_change(coins, total):
    """
    Efficiently count how many ways to make change for a total with the coins.

    This is the coin change problem described in count_coin_change_slow. This
    implementation is also recursive, resembling the implementation there, but
    much more efficient. This function relates to count_coin_change_slow in the
    same way that has_subset_sum relates to has_subset_sum_slow.
    """
    memo = {}

    def count(start, subtotal):
        if subtotal == 0:
            return 1
        if start == len(coins):
            return 0

        try:
            return memo[start, subtotal]
        except KeyError:
            result = memo[start, subtotal] = sum(
                count(start + 1, next_subtotal)
                for next_subtotal in range(subtotal, -1, -coins[start])
            )
            return result

    return count(0, total)


def count_coin_change_alt(coins, total):
    """
    Efficiently count how many ways to make change for a total with the coins.

    This alternative implementation of count_coin_change uses the same
    recursive algorithm (so it has the same asymptotic time complexity), but
    implements it using a substantially different technique. This function
    relates to count_coin_change in the same way that has_subset_sum_alt
    relates to has_subset_sum.
    """
    @functools.cache
    def count(start, subtotal):
        if subtotal == 0:
            return 1
        if start == len(coins):
            return 0
        return sum(count(start + 1, next_subtotal)
                   for next_subtotal in range(subtotal, -1, -coins[start]))

    return count(0, total)


def can_escape_forest(forest, stamina, start_i, start_j, finish_i, finish_j):
    """
    Check if the tourist can escape the Scary Forest.

    The Scary Forest is a rectangular grid represented as a sequence of strings
    (rows) in which each square (character) is a tree ('*'), an empty spot of
    trail ('.'), or a flower whose species is abbreviated by a letter. The
    tourist starts at coordinates (start_i, start_j) and must get to their
    rocket ship at (finish_i, finish_j) by moves going north, south, east, or
    west. The tourist loses a unit of stamina per move, and will sleep forever
    when it runs out, except that reaching the rocket ship with zero stamina is
    okay, because being in a rocket ship is exciting enough to wake anybody up.

    If the tourist walks into a tree, the three swallows up the tourist, who
    will then live the rest of their life inside the tree. Also, the forest is
    suspended in an infinite abyss, so to walk out of it is to fall for all
    eternity. The other matter is that, while the tourist may step on a flower,
    this makes all flowers of that species angry, and it is a productive anger:
    they all immediately grow into trees once the tourist takes another step.

    Start and finish locations are guaranteed to be empty spots of trail ('.').
    Indexing is 0-based and uses matrix conventions: the i-coordinate increases
    to the south and the j-coordinate increases to the east. Tourists find that
    to be the scariest thing of all; that's why they named it the Scary Forest.

    >>> a = ('*A.B',
    ...      '..*.',
    ...      '*B.A')
    >>> can_escape_forest(a, 5, start_i=1, start_j=0, finish_i=1, finish_j=3)
    True
    >>> can_escape_forest(a, 4, start_i=1, start_j=0, finish_i=1, finish_j=3)
    False
    >>> can_escape_forest(a, 4, start_i=1, start_j=1, finish_i=1, finish_j=3)
    True
    >>> b = ('*A.A',
    ...      '..*.',
    ...      '*B.B')
    >>> can_escape_forest(b, 5, start_i=1, start_j=0, finish_i=1, finish_j=3)
    False
    >>> can_escape_forest(b, 10, start_i=1, start_j=0, finish_i=1, finish_j=3)
    False
    >>> c = ('.........*..A..',
    ...      'QQPP*BBAA*.*...',
    ...      'ABAB*PQRQ*.*.*B',
    ...      '....*........R.',
    ...      '****..***.****C',
    ...      '...*C*....D.P.D',
    ...      '**.....*C.....D')
    >>> can_escape_forest(c, 19, start_i=3, start_j=1, finish_i=3, finish_j=14)
    True
    >>> can_escape_forest(c, 18, start_i=3, start_j=1, finish_i=3, finish_j=14)
    False
    """
    grid = [list(row) for row in forest]
    angry_flowers = set()

    def on_board(i, j):
        return 0 <= i < len(grid) and 0 <= j < len(grid[i])

    def blocked(i, j):
        return grid[i][j] == '*' or grid[i][j] in angry_flowers

    def check(i, j, remaining_stamina):
        if i == finish_i and j == finish_j:
            return True

        if not on_board(i, j) or blocked(i, j) or remaining_stamina == 0:
            return False

        if grid[i][j] == '.':
            grid[i][j] = '*'
        else:
            angry_flowers.add(grid[i][j])

        neighbors = ((i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j))
        result = any(check(h, k, remaining_stamina - 1) for h, k in neighbors)

        if grid[i][j] == '*':
            grid[i][j] = '.'
        else:
            angry_flowers.remove(grid[i][j])

        return result

    return check(start_i, start_j, stamina)


def _overestimate_escape_stamina(forest):
    """Compute an upper bound on the minimum stamina to escape a forest."""
    # The tourist can step on each empty spot and on a flower of each species.
    empty_trail_area = sum(row.count('.') for row in forest)
    species_count = len({ch for row in forest for ch in row if ch.isalpha()})
    return empty_trail_area + species_count


def min_forest_escape_stamina(forest, start_i, start_j, finish_i, finish_j):
    """
    Find the minimum stamina with which the tourist can escape the forest.

    Parameters mean the same as in can_escape_forest. If no amount of stamina
    is enough, return math.inf. One approach could be to call can_escape_forest
    with ascending stamina: 0, then 1, then 2, and so on (though you would have
    to figure out when to give up). That would find the right answer. On some
    inputs, it would even be the fastest way. But it would sometimes take too
    long. Use a different technique that is sometimes faster, even if sometimes
    slower. Reproduce at most very little logic from can_escape_forest (or its
    helpers). You can use anything from this project or the standard library.

    It's tempting to say this is only a factor of [FIXME: give it in big-O]
    slower than can_escape_forest. But it's often worse than that, because
    [FIXME: Explain. Say what can affect it. Give an example of a software
    engineering problem where this technique really does enjoy that guarantee].
    """
    def is_sufficient(stamina):
        return can_escape_forest(forest, stamina,
                                 start_i, start_j, finish_i, finish_j)

    upper_bound = _overestimate_escape_stamina(forest) + 1
    needed_stamina = first_satisfying(is_sufficient, 0, upper_bound)
    return math.inf if needed_stamina == upper_bound else needed_stamina


# TODO: Refactor this as a named tuple (namedtuple and inherit) after testing.
class _Pos:
    """Coordinates to a board square in Prance."""

    __slots__ = ('_i', '_j')

    def __init__(self, i, j):
        """Create a new player position with the specified coordinates."""
        self._i = i
        self._j = j

    def __repr__(self):
        """Representation for debugging, runnable as Python code."""
        return f'{type(self).__name__}({self.i!r}, {self.j!r})'

    def __str__(self):
        """Compact representation (not runnable as Python code)."""
        return f'{self.i},{self.j}'

    def __eq__(self, other):
        """Positions with equal corresponding coordinates are equal."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.i == other.i and self.j == other.j

    def __hash__(self):
        return hash((self.i, self.j))

    @property
    def i(self):
        """The i-coordinate (row index) of the position."""
        return self._i

    @property
    def j(self):
        """The j-coordinate (column index) of this position."""
        return self._j

    @property
    def neighbors(self):
        """Neighboring positions (but some might be off the board)."""
        yield _Pos(self.i, self.j - 1)
        yield _Pos(self.i, self.j + 1)
        yield _Pos(self.i - 1, self.j)
        yield _Pos(self.i + 1, self.j)


# TODO: Refactor this as a dataclass (via dataclass or attrs) after testing.
class _Player:
    """A player in Prance."""

    __slots__ = ('vis', 'old_pos', 'pos', 'gaffes')

    def __init__(self, start_i, start_j):
        """Create a new player with the specified starting coordinates."""
        self.vis = set()
        self.old_pos = _Pos(-1, -1)
        self.pos = _Pos(start_i, start_j)
        self.gaffes = 0

    def __repr__(self):
        """Representation for debugging. (Not runnable as Python code.)"""
        return (f'<{type(self).__name__}: vis={self.vis} '
                f'old_pos={self.old_pos} pos={self.pos} gaffes={self.gaffes}>')

    def is_blocking(self, pos):
        """Tell if a position is the current or the previous position."""
        return pos in (self.pos, self.old_pos)


class _Board:
    """Board geometry for a game of Prance."""

    __slots__ = ('_m', '_n', '_void')

    def __init__(self, m, n, vi, vj):
        """Create an m-by-n board whose void is at (vi, vj)."""
        self._m = m
        self._n = n
        self._void = _Pos(vi, vj)

    def __repr__(self):
        """Representation for debugging, runnable as Python code."""
        return (f'{type(self).__name__}({self._m!r}, {self._n!r},'
                f' {self._void.i!r}, {self._void.j!r})')

    def __contains__(self, pos):
        """Tell if a position is on the board (in bounds and not the void)."""
        return (0 <= pos.i < self._m and 0 <= pos.j < self._n
                and pos != self._void)


_MAX_GAFFES = 2
"""The maximum number of gaffes allowed to each player in a game of Prance."""


def _active_player_has_winning_strategy(board, active, inactive):
    """Tell if the active Prance player has a winning strategy in mid-game."""
    # If Inactive's move was illegal, Active calls it out and immediately wins.
    if (inactive.pos not in board or active.is_blocking(active.pos) or
            (inactive.pos in inactive.vis and inactive.gaffes == _MAX_GAFFES)):
        return True

    # Active ensures that Inactive's current and future gaffes are detected.
    gaffe = inactive.pos in inactive.vis
    if gaffe:
        inactive.gaffes += 1
    else:
        inactive.vis.add(inactive.pos)

    # Record Active's current and old position so we can backtrack the game.
    old_old_pos = active.old_pos
    active.old_pos = active.pos

    try:
        for pos in active.old_pos.neighbors:
            active.pos = pos
            if not _active_player_has_winning_strategy(board, inactive, active):
                return True  # Active can deny Inactive a winning strategy.

        return False  # Active has no way to deny Inactive a winning strategy.
    finally:
        # Restore Active's current and old position, to backtrack the game.
        active.pos = active.old_pos
        active.old_pos = old_old_pos

        # Restore Inactive's gaffe bookkeeping too. (Active is honorable.)
        if gaffe:
            inactive.gaffes -= 1
        else:
            inactive.vis.remove(inactive.pos)


def find_prance_winner(m, n, vi, vj, ai, aj, bi, bj):
    """
    Determine which player, A or B, has a winning strategy in a game of Prance.

    A player has a winning strategy if, provided they play perfectly, they are
    guaranteed to win, no matter how their opponent plays.

    A game of Prance is played on an m-by-n board with a void at (vi, vj) where
    no one can go. A starts at (ai, aj), B at (bi, bj). Players alternate
    turns. A goes first. The player whose turn it is must move up, down, left,
    or right on the board, but can't move to the void, their opponent's
    location, or their opponent's most recent previous location. Also, to move
    onto any square one has ever previously occupied is a gaffe; each player is
    allowed at most two gaffes. If a player has no legal move, their opponent
    wins. The void and players' start squares are guaranteed to be three
    different squares within the m-by-n rectangle.

    Return 'A' if A has a winning strategy, or 'B' if B has a winning strategy.
    Some player is guaranteed to have one, because [FIXME: Say why.]

    Use the simplest correct algorithm you can think of that passes all tests
    reasonably fast. But the code itself may be short or long and may use any
    combination of language features. It should be correct and easy to read.
    You might want to make and use helper functions/classes.

    >>> find_prance_winner(1, 3, 0, 0, 0, 1, 0, 2)
    'A'
    """
    board = _Board(m, n, vi, vj)
    a = _Player(ai, aj)
    b = _Player(bi, bj)
    return 'A' if _active_player_has_winning_strategy(board, a, b) else 'B'


# !!FIXME: Fix consecutive y description. (What about early game?)
def find_unfair_countdown_winner(n, holes, ax, ay, ak, af, bx, by, bk, bf):
    """
    Predict whether Alice or Bob will win their game of Unfair Countdown.

    Alice ("A") and Bob ("B") play a game of Unfair Countdown, which they
    designed and are perfect at. A player wins when their opponent loses, which
    happens when their opponent has no legal move. Alice takes the first turn.

    A counter has an initial value of n, which may be large. When Alice moves,
    she subtracts ax or ay from it; when Bob moves, he subtracts bx or by from
    it. Alice and Bob can always subtract ax and bx, respectively. Alice can
    subtract ay if she subtracted ax sometime in her last ak turns or if Bob
    has just subtracted by. Likewise, Bob can subtract by if he subtracted bx
    sometime in his last bk turns or if Alice has just subtracted ay. (That is,
    an x can always be played, and each player may play a y up to three times
    in a row and also anytime the other player has just played their y.)

    Neither player may decrease the counter below zero or to a hole (any value
    in holes). Alice may not decrease it to a positive multiple of af (Alice's
    factor). Bob may not decrease it to a positive multiple bf (Bob's factor).

    holes is a (possibly empty) set of positive ints; other parameters are
    positive ints, except n may be zero. ax != ay and bx != by. Alice and Bob
    enjoy long games, so n can be pretty big. But ax, xy, ak, bx, by, and bk
    can be assumed small. af, bf, and len(holes) may each be small or large.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    # FIXME: Needs implementation.


# !!TODO: Decide whether to defer this to a later problem set.
def count_n_queens(n):
    """
    Count the ways n queens can peacefully coexist on an n-by-n chessboard.

    A real chessboard always has n=8, but here n may also be other nonnegative
    integers. This returns the number of distinct ways to arrange n queens on
    such a board where no queen can attack another: no two queens are in the
    same rank, the same file, or the same diagonal. Space complexity is O(n).

    Symmetries count separately. For example:

    >>> count_n_queens(4)
    2

    This returns 2, not 1, even though the two ways are mirror images:

        .Q..    ..Q.
        ...Q    Q...
        Q...    ...Q
        ..Q.    .Q..

    Hint: Any time complexity is acceptable so long as the tests pass in a
    reasonable time, but some very frequent operations that are practical to
    make fast are checking if a rank, file, or diagonal is occupied. Such
    checks should take O(1) time and might be fastest if done without hashing.

    >>> [count_n_queens(n) for n in range(13)]
    [1, 1, 0, 0, 2, 10, 4, 40, 92, 352, 724, 2680, 14200]
    """
    ranks = set()
    pos_diag = set()
    neg_diag = set()
    queens = [None] * n

    def count(qi):
        if qi == n:
            return 1

        acc = 0

        for qj in range(n):
            if (qj in ranks or qi + qj in pos_diag or qi - qj in neg_diag):
                continue

            ranks.add(qj)
            pos_diag.add(qi + qj)
            neg_diag.add(qi - qj)

            queens[qi] = qj
            acc += count(qi + 1)

            ranks.remove(qj)
            pos_diag.remove(qi + qj)
            neg_diag.remove(qi - qj)

        return acc

    return count(0)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
