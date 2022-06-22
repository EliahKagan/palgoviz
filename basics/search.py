#!/usr/bin/env python

"""
Searching.

See also recursion.py.

Documentation within this module uses these conventions and simplifications:

1. When not otherwise specified, functions that process a single sequence or
   other iterable, and that are documented with a time or space complexity
   containing the variable n, use it to mean either the number of items in or
   to be processed from the input. For example, if the only parameter is values
   then n = len(values), and if there are also low and high parameters, such
   that only the region values[low:high] should be accessed, n = high - low.

2. It is often said, including in the official Python documentation and in
   docstrings on functions in this module and recursion.py, that a sequence
   must be sorted for binary search to work correctly. But the actual
   precondition is much weaker: [TODO: After doing the relevant exercises in
   this module, replace this bracketed text with a statement of the weaker
   precondition and which functions it applies to in this module.]

3. Functions that perform equality or order comparisons on their elements are
   assumed to receive elements that can be compared in O(1) time, except when
   otherwise stated or implied. These functions must still work on elements
   that take asymptotically longer to compare, but their documented time
   complexities may not hold. In such situations, big-O time complexities are
   still accurate as upper bounds on the number of comparisons performed.

4. "Numbers" passed to functions are assumed to be real-valued and to support
   all expected and generally desired operations, arithmetic and otherwise, of
   most number types in Python. It follows from this that no infinities or NaNs
   are passed, even when using types that have such values, as they are not on
   the real number line. It does not follow that their types are subclasses of
   Real or even Number. For example, they may be Decimal. They need not be
   standard library types. But within each invocation of a public function in
   this module, all numbers passed together can be assumed to be either the
   same type as each other, or otherwise arithmetically compatible.

5. For functions that solve problems about sums, implementations may assume
   that rounding error is not a problem. (Therefore, callers are heavily
   restricted in the float values they can pass, though not in int or Fraction
   values, and hardly at all in Decimal values.)

6. Where not otherwise stated, time and space complexities given for functions
   that process numbers may assume comparisons and basic arithmetic operations
   take O(1) time. This is correct for numbers of limited range and precision,
   and for ints small enough to fit in a machine word, and a good approximation
   for most, though not all, ints arising in practical applications. But be
   aware that, since Python ints may be arbitrarily big, not all of these time
   and space complexity claims will always be accurate. Basic operations on big
   ints take time linear in their operands' representation lengths, which is
   logarithmic (rather than constant) in their operands' magnitudes.
"""

import bisect
import contextlib
import functools
import itertools
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

    [FIXME: AFTER you are satisfied this solution is correct, including in time
    and space, and all tests pass, THEN review all binary search functions in
    recursion.py, and replace all this bracketed text with:

      (A) A statement of which one of them this is similar to, if any.

      (B) Taking each pair of "X" and "X_alt" as the same approach (and thus
          deciding based on factors besides endpoint exclusivity/inclusivity),
          statements, for each approach you did not use here:

          1. If you could have used it here or not, and why.

          2. For any you could've used here, any major advantages/disadvantages
             it would have, compared to the approach you did use.

          If an approach would require far more code, you should still consider
          it feasible, if you are convinced that it really can be done.

    NB: This is not about calling functions in recursion.py, which you should
    not do anywhere in this module, but about applying the approaches they take
    in implementing this function.]

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
    should use the same approach as some function in recursion.py (but not a
    function, if any, whose approach bsearch uses above, and thus also not the
    "_alt" version, if any, of such a function), unless that's not possible, as
    detailed in the text you added to the bsearch docstring.

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
    above-defined function that also doesn't use it. Do not use my_bisect_left.

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


def _two_fail(total, cause=None):
    """Raise ValueError to indicate there is no solution to a 2-sum problem."""
    raise ValueError(f'no two numbers sum to {total!r}') from cause


def two_sum_slow(numbers, total):
    """
    Find indices of two numbers that sum to total. Minimize auxiliary space.

    Although the numbers may be equal, the indices must be unequal. Give the
    left index before the right one. If there are multiple solutions, return
    any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_slow(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_slow(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_slow(a, -76)
    (5, 13)
    >>> two_sum_slow(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_slow([5, 6, 5], 10)
    (0, 2)
    """
    # Although un-Pythonic, this code avoids obscuring how the algorithm works.
    for left in range(len(numbers) - 1):
        for right in range(left + 1, len(numbers)):
            if numbers[left] + numbers[right] == total:
                return left, right

    _two_fail(total)


# !!FIXME: When removing implementation bodies, remove this entirely rather
# than making it an exercise. Tag the removal commit for possible revert later.
def two_sum_slow_alt(numbers, total):
    """
    Find indices of two numbers that sum to total. Minimize auxiliary space.

    This alternative implementation of two_sum_slow uses the same algorithm but
    implements it differently to avoid nested loops. (This can also be done
    with a comprehension and no loops, but it is not clearer.)

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_slow_alt(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_slow_alt(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_slow_alt(a, -76)
    (5, 13)
    >>> two_sum_slow_alt(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_slow_alt([5, 6, 5], 10)
    (0, 2)
    """
    pairs = itertools.combinations(enumerate(numbers), 2)

    for (left, left_value), (right, right_value) in pairs:
        if left_value + right_value == total:
            return left, right

    _two_fail(total)


# !!FIXME: When removing implementation bodies, drop the mapping_factory param.
def two_sum_fast(numbers, total, *, mapping_factory=dict):
    """
    Find indices of two numbers that sum to total. Minimize running time.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_fast(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_fast(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_fast(a, -76)
    (5, 13)
    >>> two_sum_fast(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_fast([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = [r.randrange(-2**40, 2**40) for _ in range(10**6)]
    >>> two_sum_fast(b, -63824289)
    (541756, 673938)
    >>> two_sum_fast(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    history = mapping_factory()

    for right, value in enumerate(numbers):
        try:
            left = history[total - value]
        except KeyError:
            history[value] = right
        else:
            return left, right

    _two_fail(total)


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

    _two_fail(total)


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

    >>> a = (-96, -95, -79, -76, -74, -69, -49, -48, -38, -35, -34, -27, -24,
    ...      -22, -16, -13, -11, -6, 4, 9, 18, 37, 40, 71, 72)
    >>> two_sum_sorted(a, 2) in ((5, 23), (8, 22), (9, 21), (14, 20))
    True
    >>> two_sum_sorted(a, 5) in ((9, 22), (15, 20))
    True
    >>> two_sum_sorted(a, -76)
    (6, 11)
    >>> two_sum_sorted(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_sorted([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = sorted(r.randrange(-2**40, 2**40) for _ in range(10**6))
    >>> two_sum_sorted(b, -63824289)
    (499549, 500219)
    >>> two_sum_sorted(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    return _two_sum_sorted_keyed(numbers, total, _identity_function)


# !!FIXME: When removing implementation bodies, remove this entirely rather
# than making it an exercise. Tag the removal commit for possible revert later.
def two_sum_sorted_alt(numbers, total):
    """
    Given sorted numbers, find indices of two numbers that sum to total.

    This is an alternative implementation of two_sum_sorted, satisfying the
    same requirements with the same asymptotic time and auxiliary space
    complexities. This implementation contains all its core logic, rather than
    delegating it to a helper shared with two_sum_nohash.

    >>> a = (-96, -95, -79, -76, -74, -69, -49, -48, -38, -35, -34, -27, -24,
    ...      -22, -16, -13, -11, -6, 4, 9, 18, 37, 40, 71, 72)
    >>> two_sum_sorted_alt(a, 2) in ((5, 23), (8, 22), (9, 21), (14, 20))
    True
    >>> two_sum_sorted_alt(a, 5) in ((9, 22), (15, 20))
    True
    >>> two_sum_sorted_alt(a, -76)
    (6, 11)
    >>> two_sum_sorted_alt(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_sorted_alt([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = sorted(r.randrange(-2**40, 2**40) for _ in range(10**6))
    >>> two_sum_sorted_alt(b, -63824289)
    (499549, 500219)
    >>> two_sum_sorted_alt(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    left = 0
    right = len(numbers) - 1

    while left < right:
        total_here = numbers[left] + numbers[right]
        if total_here < total:
            left += 1
        elif total_here > total:
            right -= 1
        else:
            return left, right

    _two_fail(total)


def _normalize_index_pair(left, right):
    """Return a pair of indices with the lower index first."""
    return (right, left) if right < left else (left, right)


# !!FIXME: When removing implementation bodies, drop the sort_function param.
def two_sum_nohash(numbers, total, *, sort_function=sorted):
    """
    Find indices of two numbers that sum to total, without hashing.

    Minimize running time.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_nohash(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_nohash(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_nohash(a, -76)
    (5, 13)
    >>> two_sum_nohash(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_nohash([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = [r.randrange(-2**40, 2**40) for _ in range(10**6)]
    >>> two_sum_nohash(b, -63824289)
    (541756, 673938)
    >>> two_sum_nohash(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    indices = sort_function(range(len(numbers)), key=numbers.__getitem__)
    left, right = _two_sum_sorted_keyed(indices, total, numbers.__getitem__)
    return _normalize_index_pair(indices[left], indices[right])


# !!FIXME: When removing implementation bodies, remove this entirely rather
# than making it an exercise. Tag the removal commit for possible revert later.
def two_sum_nohash_alt(numbers, total, *, sort_function=sorted):
    """
    Find indices of two numbers that sum to total, without hashing.

    This is an alternative implementation of two_sum_nohash, satisfying the
    same requirements with the same asymptotic time and auxiliary space
    complexities. This implementation contains all its core logic, rather than
    delegating to a helper shared with two_sum_sorted.

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_nohash_alt(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_nohash_alt(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_nohash_alt(a, -76)
    (5, 13)
    >>> two_sum_nohash_alt(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_nohash_alt([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = [r.randrange(-2**40, 2**40) for _ in range(10**6)]
    >>> two_sum_nohash_alt(b, -63824289)
    (541756, 673938)
    >>> two_sum_nohash_alt(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    decorated = sort_function(enumerate(numbers), key=operator.itemgetter(1))

    left = 0
    right = len(decorated) - 1

    while left < right:
        left_old_index, left_value = decorated[left]
        right_old_index, right_value = decorated[right]
        total_here = left_value + right_value

        if total_here < total:
            left += 1
        elif total_here > total:
            right -= 1
        else:
            return _normalize_index_pair(left_old_index, right_old_index)

    _two_fail(total)


# !!FIXME: When removing implementation bodies, remove this entirely rather
# than making it an exercise. Tag the removal commit for possible revert later.
def two_sum_nohash_alt2(numbers, total, *, sort_function=sorted):
    """
    Find indices of two numbers that sum to total, without hashing.

    This is a second alternative implementation of two_sum_nohash, satisfying
    the same requirements with the same asymptotic time and auxiliary space
    complexities. This implementation delegates directly to two_sum_sorted_alt,
    rather than delegating to a deliberately generalized nonpublic function
    shared with two_sum_sorted (as two_sum_nohash does) or containing all its
    core logic (as two_sum_nohash_alt does).

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_nohash_alt2(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_nohash_alt2(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_nohash_alt2(a, -76)
    (5, 13)
    >>> two_sum_nohash_alt2(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_nohash_alt2([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = [r.randrange(-2**40, 2**40) for _ in range(10**6)]
    >>> two_sum_nohash_alt2(b, -63824289)
    (541756, 673938)
    >>> two_sum_nohash_alt2(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    sorted_numbers = sort_function(numbers)
    left, right = two_sum_sorted_alt(sorted_numbers, total)
    left_value = sorted_numbers[left]
    right_value = sorted_numbers[right]
    left_old_index = numbers.index(left_value)
    if left_value == right_value:
        return left_old_index, numbers.index(right_value, left_old_index + 1)
    return _normalize_index_pair(left_old_index, numbers.index(right_value))


# FIXME: Having implemented two_sum_slow, two_sum_fast, two_sum_sorted, and
# two_sum_nohash, if any of them have substantial overlapping logic, extract it
# to one or more nonpublic module-level functions. (Ensure tests still pass.)
# If this is better, keep it. Otherwise, revert it, and briefly state in one or
# more functions' docstrings why you're retaining duplicate or similar logic.

# FIXME: Some of two_sum_slow, two_sum_fast, two_sum_sorted, and two_sum_nohash
# may use an algorithm or data structure you've implemented something similar
# to (with the same asymptotic worst-case time complexity) in this project, or
# intend to add in the future. There may be more than one such algorithm or
# data structure. But each of your 2-sum functions involves at most one. Modify
# the signature of each such 2-sum function to use dependency injection, so the
# caller may specify an implementation. When the caller does not, the standard
# library implementation should still be used (and all tests continue to pass).
# Where feasible, add tests with the implementation from this project. When
# that is not feasible, comment (near where you'd add them) to explain why not.


def two_sum_int_narrow(numbers, total):
    """
    Find indices of two bounded integers that sum to total, without hashing.

    Elements of numbers, and the total, are ints. The algorithm must be correct
    for any number of integers of any values but need not be reasonable to use
    if m = max(numbers) - min(numbers) + 1 [the range of values in numbers] is
    much larger than n. When m is small, this should in practice be as fast as
    hashing, and often faster.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_int_narrow(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_int_narrow(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_int_narrow(a, -76)
    (5, 13)
    >>> two_sum_int_narrow(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_int_narrow([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = [r.randrange(-2997, 2500, 2) for _ in range(10**6)]
    >>> left, right = two_sum_int_narrow(b, 2574)
    >>> b[left] + b[right]
    2574
    >>> two_sum_int_narrow(b, 2573)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 2573
    """
    try:
        minimum = min(numbers)
        maximum = max(numbers)
    except ValueError as error:
        _two_fail(total, error)

    history = [None] * (maximum - minimum + 1)

    for right, value in enumerate(numbers):
        complement = total - value
        if not minimum <= complement <= maximum:
            continue
        left = history[complement - minimum]
        if left is not None:
            return left, right
        history[value - minimum] = right

    _two_fail(total)


class _Node:
    """Node in a base-b digit trie (prefix tree). Helper for _Trie."""

    __slots__ = ('children', 'value')

    def __init__(self, b):
        self.children = [None] * b
        self.value = None


class _Trie:
    """Special-purpose base-b digit trie (prefix tree), for two_sum_int."""

    __slots__ = ('_b', '_root')

    def __init__(self, b):
        """Create an initially empty trie."""
        self._b = b
        self._root = _Node(b)

    def __getitem__(self, key):
        """Get the value associated with a nonnegative integer key, if any."""
        assert key >= 0, 'Negative key accidentally used as _Trie subscript.'

        suffix = key
        node = self._root
        b = self._b  # FIXME: Factor this out if it doesn't improve speed.

        while suffix != 0 and node is not None:
            suffix, index = divmod(suffix, b)
            node = node.children[index]

        if node is None or node.value is None:
            raise KeyError(key)

        return node.value

    def __setitem__(self, key, value):
        """Associate a value (can't be None) with a nonnegative integer key."""
        assert key >= 0, 'Negative key accidentally used as _Trie subscript.'

        suffix = key
        node = self._root
        b = self._b  # FIXME: Factor this out if it doesn't improve speed.

        while suffix != 0:
            suffix, index = divmod(suffix, b)
            child = node.children[index]
            if child is None:
                child = node.children[index] = _Node(b)
            node = child

        node.value = value


class _BiTrie:
    """Special-purpose mapping-like type using two tries, for two_sum_int."""

    __slots__ = dict(_pos='Trie whose keys are positive numbers and zero.',
                     _neg='Trie whose keys are negated negative numbers.')

    def __init__(self, b):
        """Create an initially empty mapping based on a pair of tries."""
        self._pos = _Trie(b)
        self._neg = _Trie(b)

    def __getitem__(self, key):
        """Get the value associated with an integer key, if any."""
        return self._neg[-key] if key < 0 else self._pos[key]

    def __setitem__(self, key, value):
        """Associate a value (can't be None) with an integer key."""
        if key < 0:
            self._neg[-key] = value
        else:
            self._pos[key] = value


# !!FIXME: When removing implementation bodies, replace the table with a fixme
# saying the table has spoilers and what tag name to revert to get it. Commit
# the replacement by itself and tag the commit, naming the tag accordingly.
def two_sum_int(numbers, total, *, b=2):
    """
    Find indices of two integers that sum to total, by making b-way choices.

    Elements of numbers, and the total, are ints. The "branching ratio" b is an
    int and at least 2 (since a 1-way choice is not a choice). When b is small
    (say, under 50), this is a practical even on many and/or big numbers, but
    slower in practice than two_sum_fast or two_sum_nohash. (With any b, this
    may still make some 2-way choices: if-statements and loops are permitted.)

    This involves substantial logic not used by other 2-sum functions. It does
    not use hashing. It does not use order comparisons, except it may use them
    to generalize a solution for when all(0 <= x <= total for x in numbers) to
    work with arbitrary integers. It doesn't work around these restrictions by
    simulating hashing or order comparisons in terms of other operations. Like
    two_sum_fast, this needs just one left-to-right pass through numbers, and
    after two numbers that add to total are found, iteration need not continue.

    This function's performance characteristics depend on the magnitudes of the
    numbers in its input. While true of all the other 2-sum functions too, here
    it's relevant even for numbers that fit in a machine word. Yet, like most
    others, this should do okay even with larger numbers. Consider this table:

    |         | slow         | fast         | sorted     | nohash           | int_narrow     | int                      |
    |---------|--------------|--------------|------------|------------------|----------------|--------------------------|
    | ops.    | (none)       | hash, -      | <, >       | <, >             | <=, -          | [FIXME: Fill this in.]   |
    | algo/ds | (none)       | dict         | (none)     | sorted           | list           | (custom)                 |
    | branch  | 2            | O(n)         | 2          | 2                | m              | b                        |
    | time    | O(n^2 log M) | O(n log M)   | O(n log M) | O(n log n log M) | O(m + n log M) | O(n (b + log M) log_b M) |
    | ~ time  | O(n^2)       | O(n)         | O(n)       | O(n log n)       | O(m + n)       | O(n b log_b M)           |
    | space   | O(log M)     | O(n + log M) | O(1)       | O(n)             | O(m + log M)   | O(n b log_b M + log M)   |
    | ~ space | O(1)         | O(n)         | O(1)       | O(n)             | O(m)           | O(n b log_b M)           |

    In the table, M is the maximum magnitude of any value in numbers or total.
    If total and most numbers are smaller than M, all functions are faster than
    shown. Indexing and index arithmetic are taken to be O(1) for any n. With
    hashing, good hash distribution is assumed, and times hold with high
    probability. Space is auxiliary (not total). "~" time/space are when values
    fit in machine words. Otherwise, arithmetic takes O(log M) time and space,
    and comparisons take O(log M) time and are assumed to take O(1) space. The
    "ops." row only lists operations useful to distinguish the approaches.

    FIXME: This table may have errors and is based on my solutions. Closely
    check all its claims about previous 2-sum implementations. That can be done
    collaboratively. I think the table will help in designing this algorithm.

    FIXME: Once this returns correct results, optimize your code to make it
    faster. One avenue of optimization is to tune the default value of b.

    >>> a = (-79, -48, -96, -22, -11, -27, -34, 40, 37, 18, -38, -76, -6, -49,
    ...      -74, -69, -16, 72, 9, -13, 4, -24, -95, -35, 71)
    >>> two_sum_int(a, 2) in ((7, 10), (8, 23), (9, 16), (15, 24))
    True
    >>> two_sum_int(a, 5) in ((7, 23), (9, 19))
    True
    >>> two_sum_int(a, -76)
    (5, 13)
    >>> two_sum_int(a, 8)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to 8
    >>> two_sum_int([5, 6, 5], 10)
    (0, 2)

    >>> import random
    >>> r = random.Random(7278875518357631735)
    >>> b = [r.randrange(-2**40, 2**40) for _ in range(10**6)]
    >>> two_sum_int(b, -63824289)
    (541756, 673938)
    >>> two_sum_int(b, -63824288)
    Traceback (most recent call last):
      ...
    ValueError: no two numbers sum to -63824288
    """
    return two_sum_fast(numbers, total, mapping_factory=lambda: _BiTrie(b))


# FIXME: The algorithm in two_sum_int tends to be slower than the algorithms in
# two_sum_fast and two_sum_nohash for reasons other than asymptotic time
# complexity, mainly due to its poor cache locality, but also inefficiencies of
# expressing it in Python. So if it were accidentally implemented wrong and ran
# moderately slower for that reason, you might not know. Augment the above code
# to support visualization, then visualize a run of two_sum_int (or the effect
# of such a run) on a small input.


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

    FIXME: Needs tests.
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

    FIXME: Needs tests.
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

    FIXME: Needs tests.
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

    >>> count_coin_change_slow([2, 3, 5], 500)
    4251
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

    >>> count_coin_change([1, 2, 2], 5)
    6
    >>> count_coin_change([2, 3, 5], 500)
    4251
    >>> c = [3, 13, 77, 16, 8, 19, 2, 44, 43, 95, 97, 101, 102, 33, 36, 21, 14]
    >>> count_coin_change(c, 489)
    1801044124
    >>> count_coin_change([17, 2, 19, 3, 13, 682], 4213)
    960417883
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

    >>> count_coin_change_alt([1, 2, 2], 5)
    6
    >>> count_coin_change_alt([2, 3, 5], 500)
    4251
    >>> c = [3, 13, 77, 16, 8, 19, 2, 44, 43, 95, 97, 101, 102, 33, 36, 21, 14]
    >>> count_coin_change_alt(c, 489)
    1801044124
    >>> count_coin_change_alt([17, 2, 19, 3, 13, 682], 4213)
    960417883
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
    engineering problem where this technique really does enjoy that guarantee.]

    FIXME: Needs tests.
    """
    def is_sufficient(stamina):
        return can_escape_forest(forest, stamina,
                                 start_i, start_j, finish_i, finish_j)

    upper_bound = _overestimate_escape_stamina(forest) + 1
    needed_stamina = first_satisfying(is_sufficient, 0, upper_bound)
    return math.inf if needed_stamina == upper_bound else needed_stamina


# TODO: Refactor this as a named tuple (namedtuple and inherit) after testing.
class _Pos:
    """Coordinates to a board square in a game of A Void."""

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
        return (_Pos(self.i, self.j - 1), _Pos(self.i, self.j + 1),
                _Pos(self.i - 1, self.j), _Pos(self.i + 1, self.j))


# TODO: Refactor this as a data class (via dataclass or attrs) after testing.
class _AVPlayer:
    """A player in a game of A Void."""

    __slots__ = ('vis', 'old_pos', 'pos', 'gaffes')

    def __init__(self, start_i, start_j):
        """Create a new player with the specified starting coordinates."""
        self.old_pos = None
        self.pos = _Pos(start_i, start_j)
        self.vis = {self.pos}
        self.gaffes = 0

    def __repr__(self):
        """Representation for debugging. (Not runnable as Python code.)"""
        return (f'<{type(self).__name__}: vis={self.vis} '
                f'old_pos={self.old_pos} pos={self.pos} gaffes={self.gaffes}>')


class _AVBoard:
    """Board geometry for a game of A Void."""

    __slots__ = ('_m', '_n', '_void')

    def __init__(self, m, n, vi, vj):
        """Create an m-by-n board whose void is at (vi, vj)."""
        self._m = m
        self._n = n
        self._void = _Pos(vi, vj)
        if not self._in_bounds(self._void):
            raise ValueError('the void is outside the board rectangle')

    def __repr__(self):
        """Representation for debugging, runnable as Python code."""
        return (f'{type(self).__name__}({self._m!r}, {self._n!r},'
                f' {self._void.i!r}, {self._void.j!r})')

    def __contains__(self, pos):
        """Tell if a position is on the board (in bounds and not the void)."""
        return self._in_bounds(pos) and pos != self._void

    def _in_bounds(self, pos):
        return 0 <= pos.i < self._m and 0 <= pos.j < self._n


_MAX_GAFFES = 2
"""The maximum number of gaffes allowed to each player in a game of A Void."""


def _a_wins_av(board, a, b):
    """Tell if "A" has a winning strategy in mid-game of A Void."""
    win = False
    old_old_pos = a.old_pos
    a.old_pos = a.pos

    for a.pos in a.old_pos.neighbors:
        if a.pos not in board or a.pos in (b.pos, b.old_pos):
            continue

        if a.pos not in a.vis:
            gaffe = False
            a.vis.add(a.pos)
        elif a.gaffes < _MAX_GAFFES:
            gaffe = True
            a.gaffes += 1
        else:
            continue

        win = not _a_wins_av(board, a=b, b=a)

        if gaffe:
            a.gaffes -= 1
        else:
            a.vis.remove(a.pos)

        if win:
            break

    a.pos = a.old_pos
    a.old_pos = old_old_pos
    return win


def find_av_winner(m, n, vi, vj, ai, aj, bi, bj):
    """
    Determine which player, A or B, has a winning strategy in a game of A Void.

    A player has a winning strategy if, provided they play perfectly, they are
    guaranteed to win, no matter how their opponent plays.

    A Void is played on an m-by-n board with a void at (vi, vj) where no one
    can go. A starts at (ai, aj), B at (bi, bj). Players alternate turns. A
    goes first. The player whose turn it is must move up, down, left, or right
    on the board, but can't move to the void, their opponent's location, or
    their opponent's most recent previous location. Also, to move onto any
    square one has ever previously occupied is a gaffe; each player is allowed
    at most two gaffes. If a player has no legal move, their opponent wins. The
    void and players' start squares are guaranteed to be three different
    squares within the m-by-n rectangle.

    Return 'A' if A has a winning strategy, or 'B' if B has a winning strategy.
    Some player is guaranteed to have one, because [FIXME: Say why.]

    Use the simplest correct algorithm you can think of that passes all tests
    reasonably fast. But the code itself may be short or long and may use any
    combination of language features. It should be correct and easy to read.
    You might want to make and use helper functions/classes.

    FIXME: Verify tests, and add more elsewhere.

    >>> find_av_winner(m=1, n=3, vi=0, vj=0, ai=0, aj=1, bi=0, bj=2)
    'B'
    >>> find_av_winner(m=3, n=3, vi=1, vj=2, ai=0, aj=0, bi=2, bj=2)
    'A'
    >>> find_av_winner(m=4, n=3, vi=1, vj=2, ai=0, aj=0, bi=2, bj=2)
    'B'
    >>> find_av_winner(m=3, n=4, vi=1, vj=3, ai=0, aj=3, bi=2, bj=2)
    'B'
    >>> find_av_winner(m=3, n=4, vi=2, vj=3, ai=1, aj=0, bi=0, bj=1)
    'A'
    """
    board = _AVBoard(m, n, vi, vj)
    a = _AVPlayer(ai, aj)
    b = _AVPlayer(bi, bj)
    if a.pos not in board or b.pos not in board or a.pos == b.pos:
        raise ValueError("players starts must differ and be on the board")
    return 'A' if _a_wins_av(board, a=a, b=b) else 'B'


# !!NOTE: When removing implementation bodies, KEEP THIS ENTIRE FUNCTION.
def count_av_a_wins(m, n, *, searcher=find_av_winner, verbose=True):
    """
    Display and count A Void games where B has a winning strategy.

    On most board dimensions, A Void somewhat favors B. This uses
    find_av_winner to find the starting configurations where A has the winning
    strategy. (This further tests find_av_winner and may help in debugging it.)

    >>> count_av_a_wins(2, 3, verbose=False)
    A won 68 out of 120 games.
    >>> count_av_a_wins(3, 2, verbose=False)
    A won 68 out of 120 games.
    >>> count_av_a_wins(2, 4, verbose=False)
    A won 156 out of 336 games.
    >>> count_av_a_wins(4, 2, verbose=False)
    A won 156 out of 336 games.
    >>> count_av_a_wins(2, 5, verbose=False)  # A bit slow.  # doctest: +SKIP
    A won 272 out of 720 games.
    >>> count_av_a_wins(5, 2, verbose=False)  # A bit slow.  # doctest: +SKIP
    A won 272 out of 720 games.
    >>> count_av_a_wins(3, 4, verbose=False)  # Very slow.  # doctest: +SKIP
    A won 420 out of 1320 games.
    >>> count_av_a_wins(4, 3, verbose=False)  # Very slow.  # doctest: +SKIP
    A won 420 out of 1320 games.
    """
    total = b_wins = 0

    positions = itertools.product(range(m), range(n))

    for (vi, vj), (ai, aj), (bi, bj) in itertools.permutations(positions, 3):
        total += 1
        winner = searcher(m, n, vi, vj, ai, aj, bi, bj)
        if winner == 'B':
            continue
        if winner != 'A':
            raise AssertionError(f"winner is {winner!r}, should be 'A' or 'B'")
        b_wins += 1
        if verbose:
            print(f'A wins {vi=}, {vj=}, {ai=}, {aj=}, {bi=}, {bj=}')

    if total == 1:
        print(f'A won {b_wins} out of {total} game.')
    else:
        print(f'A won {b_wins} out of {total} games.')


class _IMDPlayer:
    """
    Unchanging parameters for a player in I Must Decline.

    _IMDPlayer instances use reference equality comparisons.
    """

    __slots__ = ('x', 'y', 'k', 'f')

    def __init__(self, x, y, k, f):
        """Create the unchanging parameters for one player."""
        self.x = x
        self.y = y
        self.k = k
        self.f = f

    def __repr__(self):
        """Representation for debugging. Runnable as Python code."""
        return (type(self).__name__
                + f'(x={self.x!r}, y={self.y!r}, k={self.k!r}, f={self.f!r})')


def _a_wins_imd(holes, memo, a, b, i, ay_run, by_run):
    """Tell if "Alice" has a winning strategy in mid-game of I Must Decline."""
    with contextlib.suppress(KeyError):
        return memo[a, b, i, ay_run, by_run]

    def can_go(new_i):
        return (new_i >= 0 and (new_i % a.f != 0 or new_i == 0)
                and new_i not in holes)

    win = memo[a, b, i, ay_run, by_run] = (
        # Can "A" play a.x to win?
        (can_go(i - a.x) and
            not _a_wins_imd(holes, memo, a=b, b=a, i=(i - a.x),
                            ay_run=by_run, by_run=0)) or
        # Can "A" play a.y to win?
        (can_go(i - a.y) and (ay_run < a.k or by_run > 0) and
            not _a_wins_imd(holes, memo, a=b, b=a, i=(i - a.y),
                            ay_run=by_run, by_run=min(ay_run + 1, a.k)))
    )

    return win


def find_imd_winner(i, holes, ax, ay, ak, af, bx, by, bk, bf):
    """
    Predict who, Alice or Bob, will win a game of I Must Decline.

    Alice ("A") and Bob ("B") play a game of I Must Decline, which they
    designed and are perfect at. A player wins when the opposing player has no
    legal move. Return 'A' if Alice will win, or 'B' if Bob will win.

    A counter starts at i and can't be decreased below 0 or to a hole. Alice
    can't decrease it to a positive multiple of af (Alice's factor). Bob can't
    decrease it to a positive multiple bf (Bob's factor). Alice takes the first
    turn. When Alice moves, she decreases the counter by ax or ay. When Bob
    moves, he decreases it by bx or by. Alice can always subtract ax, but she
    can't subtract ay on more than ak consecutive turns, except when Bob has
    just subtracted by. Bob can always subtract bx, but he can't subtract by on
    more than bk consecutive turns, except when Alice has just subtracted ay.

    In example 1 below, Bob wins, because Alice can't decrease the counter to
    positive even numbers, and with ax=1, ay=2, and ak=3, she can't skip over
    evens more than 3 times in a row unless Bob blunders by overplaying his y:

    >>> find_imd_winner(20, set(), 1, 2, 3, 2, 4, 2, 2, 7)  # Example 1
    'B'

    In example 2 below, Alice still can't decrease the counter to positive even
    numbers, but ax=2 and ay=1, so she can easily skip them. She wins even
    though Bob is more powerful than before (bk=8 instead of bk=2):

    >>> find_imd_winner(20, set(), 2, 1, 1, 2, 4, 2, 8, 7)  # Example 2
    'A'

    holes is a (possibly empty) set of positive ints; other parameters are
    positive ints, except n may be zero. ax != ay and bx != by. Alice and Bob
    enjoy long games, so n can be pretty big. But ax, xy, ak, bx, by, and bk
    can be assumed small. af, bf, and len(holes) may each be small or large.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]

    FIXME: Verify tests. Move some elsewhere. Ensure test coverage of game
    instances where any recursive implementation has call depth 800 to 985.

    >>> find_imd_winner(10, set(), 2, 3, 3, 17, 3, 2, 3, 31)
    'B'
    >>> find_imd_winner(10, {5}, 2, 3, 3, 17, 3, 2, 3, 31)
    'A'
    >>> holes = {940, 941, 942, 944, 945, 946, 949, 950, 951, 952}
    >>> find_imd_winner(985, holes, 2, 3, 3, 17, 3, 2, 3, 31)
    'A'
    >>> find_imd_winner(985, {5}, 2, 3, 3, 17, 3, 2, 3, 31)
    'B'
    >>> find_imd_winner(979, set(), 2, 1, 3, 114, 2, 1, 3, 114)
    'A'
    >>> find_imd_winner(14783, set(), 15, 17, 4, 2279, 16, 18, 4, 2279)
    'B'
    >>> find_imd_winner(14784, set(), 15, 17, 4, 2279, 16, 18, 4, 2279)
    'A'
    """
    a = _IMDPlayer(ax, ay, ak, af)
    b = _IMDPlayer(bx, by, bk, bf)
    memo = {}
    a_wins = _a_wins_imd(holes, memo, a=a, b=b, i=i, ay_run=0, by_run=0)
    return 'A' if a_wins else 'B'


def count_n_queens_solutions(n):
    """
    Count the ways n queens can peacefully coexist on an n-by-n chessboard.

    A real chessboard always has n=8, but here n may also be other nonnegative
    integers. This returns the number of distinct ways to arrange n queens on
    such a board where no queen can attack another: no two queens are in the
    same rank, the same file, or the same diagonal. Space complexity is O(n).

    Symmetries count separately. For example:

    >>> count_n_queens_solutions(4)
    2

    This returns 2, not 1, even though the two ways are mirror images:

        .Q..    ..Q.
        ...Q    Q...
        Q...    ...Q
        ..Q.    .Q..

    Hint: Any time complexity is acceptable so long as the tests pass in a
    reasonable time, but some very frequent operations that are practical to
    make fast are checking if a rank, file, or diagonal is occupied. Each such
    check should take O(1) time and might be fastest if done without hashing.

    >>> [count_n_queens_solutions(n) for n in range(13)]
    [1, 1, 0, 0, 2, 10, 4, 40, 92, 352, 724, 2680, 14200]
    """
    if n == 0:
        return 1

    ranks = [False] * n  # Indexed 0, ..., n - 1.
    pos_diag = [False] * (n * 2 - 1)  # Indexed 0, ..., n * 2 - 2.
    neg_diag = [False] * (n * 2 - 1)  # Indexed -n + 1, ..., n - 1.

    def count(qi):
        if qi == n:
            return 1

        acc = 0

        for qj in range(n):
            if ranks[qj] or pos_diag[qi + qj] or neg_diag[qi - qj]:
                continue

            ranks[qj] = pos_diag[qi + qj] = neg_diag[qi - qj] = True
            acc += count(qi + 1)
            ranks[qj] = pos_diag[qi + qj] = neg_diag[qi - qj] = False

        return acc

    def start_count(qj):
        ranks[qj] = pos_diag[qj] = neg_diag[-qj] = True
        result = count(1)
        ranks[qj] = pos_diag[qj] = neg_diag[-qj] = False
        return result

    total = 2 * sum(start_count(qj) for qj in range(n // 2))
    return total if n % 2 == 0 else total + start_count(n // 2)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
