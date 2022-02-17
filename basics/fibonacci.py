#!/usr/bin/env python

"""
Fibonacci sequence - computation and analysis/visualization

See also the visualizations in subproblems.ipynb.

For the command-line Fibonacci numbers program that calls fib_n, see fib.py.
"""

import itertools
from decorators import memoize

def fibonacci(n):
    """
    Simple (naive) recursive Fibonacci algorithm.

    This computes the Fibonacci number F(n) in exponential time.

    >>> fibonacci(0)
    0
    >>> fibonacci(1)
    1
    >>> fibonacci(2)
    1
    >>> fibonacci(3)
    2
    >>> fibonacci(10)
    55
    >>> fibonacci_cached_4(100)  # Too big without memoization.  # doctest: +SKIP
    354224848179261915075
    >>> fibonacci(500)  # Also too big without memoization.  # doctest: +SKIP
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_cached_1(n):
    """
    Memoized recursive Fibonacci algorithm, directly based on the naive code.

    This computes the Fibonacci number F(n) in linear time.

    >>> fibonacci_cached_1(0)
    0
    >>> fibonacci_cached_1(1)
    1
    >>> fibonacci_cached_1(2)
    1
    >>> fibonacci_cached_1(3)
    2
    >>> fibonacci_cached_1(10)
    55
    >>> fibonacci_cached_1(100)
    354224848179261915075
    >>> fibonacci_cached_1(500)
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    cache = {}

    def helper(k):
        if k not in cache:
            if k == 0 or k == 1:
                cache[k] = k
            else:
                cache[k] = helper(k - 1) + helper(k - 2)

        return cache[k]

    return helper(n)


def fibonacci_cached_2(n):
    """
    Memoized recursive Fibonacci algorithm, seeding the cache with base cases.

    This computes the Fibonacci number F(n) in linear time.

    >>> fibonacci_cached_2(0)
    0
    >>> fibonacci_cached_2(1)
    1
    >>> fibonacci_cached_2(2)
    1
    >>> fibonacci_cached_2(3)
    2
    >>> fibonacci_cached_2(10)
    55
    >>> fibonacci_cached_2(100)
    354224848179261915075
    >>> fibonacci_cached_2(500)
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    cache = {0: 0, 1: 1}

    def helper(k):
        if k not in cache:
            cache[k] = helper(k - 1) + helper(k - 2)

        return cache[k]

    return helper(n)


def fibonacci_cached_3(n):
    """
    Memoized recursive Fibonacci algorithm, without caching the base cases.

    This computes the Fibonacci number F(n) in linear time.

    >>> fibonacci_cached_3(0)
    0
    >>> fibonacci_cached_3(1)
    1
    >>> fibonacci_cached_3(2)
    1
    >>> fibonacci_cached_3(3)
    2
    >>> fibonacci_cached_3(10)
    55
    >>> fibonacci_cached_3(100)
    354224848179261915075
    >>> fibonacci_cached_3(500)
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    cache = {}

    def helper(k):
        if k == 0 or k == 1:
            return k

        if k not in cache:
            cache[k] = helper(k - 1) + helper(k - 2)

        return cache[k]

    return helper(n)


@memoize
def fibonacci_cached_4(n):
    """
    Memoized recursive Fibonacci algorithm. Fourth way.

    This computes the Fibonacci number F(n) in linear time.

    >>> fibonacci_cached_4(0)
    0
    >>> fibonacci_cached_4(1)
    1
    >>> fibonacci_cached_4(2)
    1
    >>> fibonacci_cached_4(3)
    2
    >>> fibonacci_cached_4(10)
    55
    >>> fibonacci_cached_4(100)  # FIXME: Memoization should solve this.  # doctest: +SKIP
    354224848179261915075
    >>> fibonacci_cached_4(500)  # Mutual-recursion RecursionError.  # doctest: +SKIP
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_cached_4(n - 1) + fibonacci_cached_4(n - 2)


def fibonacci_short(n):
    """
    Compute Fibonacci with the simple recursive algorithm but more compactly.

    This takes advantage of the coincidence that its base cases are fixed points.

    >>> fibonacci_short(0)
    0
    >>> fibonacci_short(1)
    1
    >>> fibonacci_short(2)
    1
    >>> fibonacci_short(3)
    2
    >>> fibonacci_short(10)
    55
    """
    return n if n < 2 else fibonacci_short(n - 2) + fibonacci_short(n - 1)


def fibonacci_alr(n):
    """
    Show how arm's length recursion is very poorly suited to Fibonacci.

    This computes the Fibonacci number F(n) using the simple recursive
    algorithm, except that arm's length recursion (also called "short
    circuiting the base case") is used. This technique is especially poorly
    suited to Fibonacci, since the presence of multiple base cases leads to
    code duplication and a greater than usual increase in code complexity.

    This has the same time complexity as fibonacci() above, since arm's length
    recursion never changes that, but it may differ by a constant factor. Here,
    it is most likely slower, rather than faster, than the simpler approach.

    >>> fibonacci_alr(0)
    0
    >>> fibonacci_alr(1)
    1
    >>> fibonacci_alr(2)
    1
    >>> fibonacci_alr(3)
    2
    >>> fibonacci_alr(10)
    55
    """
    def do_fib(k):
        if k == 2:  # k - 2 == 0
            a = 0
        elif k == 3:  # k - 2 == 1
            a = 1
        else:
            a = do_fib(k - 2)

        if k == 1:  # k - 1 == 0
            b = 0
        elif k == 2:  # k - 1 == 1
            b = 1
        else:
            b = do_fib(k - 1)

        return a + b

    if n == 0:
        return 0
    if n == 1:
        return 1
    return do_fib(n)


def fibonacci_short_alr(n):
    """
    Compute the Fibonacci number F(n) with arm's length recursion more compactly.

    This is like fibonacci_short() but uses arm's length recursion. Since there
    is only one base-case condition here, this looks more like arm's length
    recursion when it is usually used. However, like many applications of arm's
    length recursion, this approach to Fibonacci would be very hard to justify.

    >>> fibonacci_short_alr(0)
    0
    >>> fibonacci_short_alr(1)
    1
    >>> fibonacci_short_alr(2)
    1
    >>> fibonacci_short_alr(3)
    2
    >>> fibonacci_short_alr(10)
    55
    """
    def do_fib(k):
        a = k - 2 if k < 4 else do_fib(k - 2)  # k < 4 iff k - 2 < 2
        b = k - 1 if k < 3 else do_fib(k - 1)  # k < 3 iff k - 1 < 2
        return a + b

    return n if n < 2 else do_fib(n)


def fibonacci_tail(n):
    """
    Tail-recursive Fibonacci implementation. This is bottom-up and linear time.

    Note that Python does not have proper tail calls, and CPython does not
    eliminate or optimize tail calls in even the simplest tail-recursive
    functions. So, while they use different techniques, this and the recursive
    memoized top-down solution both raise RecursionError for large enough n.

    >>> fibonacci_tail(0)
    0
    >>> fibonacci_tail(1)
    1
    >>> fibonacci_tail(2)
    1
    >>> fibonacci_tail(3)
    2
    >>> fibonacci_tail(10)
    55
    >>> fibonacci_tail(500)
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    def do_fib(a, b, k):
        return b if k == 1 else do_fib(b, a + b, k - 1)

    return 0 if n == 0 else do_fib(0, 1, n)


# TODO: When we do unittest and pytest, translate these doctests and observe
#       how much clearer (and easier to get right) they are.
def fib_n_clunk(n):
    """
    Return an iterator that yields the first n Fibonacci numbers.

    This uses the linear-time iterative bottom-up algorithm.

    >>> next(fib_n_clunk(0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> it = fib_n_clunk(1)
    >>> next(it)
    0
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> it = fib_n_clunk(2)
    >>> next(it)
    0
    >>> next(it)
    1
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(fib_n_clunk(1))
    [0]
    >>> list(fib_n_clunk(3))
    [0, 1, 1]
    >>> list(fib_n_clunk(4))
    [0, 1, 1, 2]
    >>> list(fib_n_clunk(7))
    [0, 1, 1, 2, 3, 5, 8]
    >>> list(fib_n_clunk(16))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    >>> list(fib_n_clunk(101))[-1]
    354224848179261915075
    >>> fib_n_clunk(-1)
    Traceback (most recent call last):
      ...
    ValueError: can't yield negatively many Fibonacci numbers
    >>> fib_n_clunk(-1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> list(fib_n_clunk(True))  # OK, since bool is a subclass of int.
    [0]
    """
    if not isinstance(n, int):
        raise TypeError('n must be an int')

    if n < 0:
        raise ValueError(f"can't yield negatively many Fibonacci numbers")

    def generate():
        if n == 0:
            return

        a = 0
        yield a
        if n == 1:
            return

        b = 1
        yield b
        if n == 2:
            return

        for _ in range(n - 2):
            a, b = b, a + b
            yield b

    return generate()


def fib():
    """
    Return an iterator for the entire (infinite) Fibonacci sequence.

    >>> it = fib()
    >>> next(it)
    0
    >>> next(it)
    1
    >>> next(it)
    1
    >>> next(it)
    2
    >>> next(it)
    3
    >>> next(it)
    5
    >>> next(it)
    8
    """
    a = 0
    b = 1
    while True:
        yield a
        a, b = b, a + b


def fib_n(n):
    """
    Return an iterator that yields the first n Fibonacci numbers.

    This uses the linear-time iterative bottom-up algorithm.

    >>> next(fib_n(0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> it = fib_n(1)
    >>> next(it)
    0
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> it = fib_n(2)
    >>> next(it)
    0
    >>> next(it)
    1
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(fib_n(1))
    [0]
    >>> list(fib_n(3))
    [0, 1, 1]
    >>> list(fib_n(4))
    [0, 1, 1, 2]
    >>> list(fib_n(7))
    [0, 1, 1, 2, 3, 5, 8]
    >>> list(fib_n(16))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    >>> list(fib_n(101))[-1]
    354224848179261915075
    >>> fib_n(-1)
    Traceback (most recent call last):
      ...
    ValueError: can't yield negatively many Fibonacci numbers
    >>> fib_n(-1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> list(fib_n(True))  # OK, since bool is a subclass of int.
    [0]
    """
    if not isinstance(n, int):
        raise TypeError('n must be an int')

    if n < 0:
        raise ValueError(f"can't yield negatively many Fibonacci numbers")

    return itertools.islice(fib(), n)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
