#!/usr/bin/env python

"""
Fibonacci sequence - computation and analysis/visualization

See also the visualizations in subproblems.ipynb.

For the command-line Fibonacci numbers program that calls fib_n, see fib.py.
"""

import itertools


def fibonacci(n):
    """
    Recursively compute the Fibonacci number F(n), where F(0) = 0, F(1) = 1.

    This is the naive exponential-time simple recursive algorithm.

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
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_cached_1(n):
    """
    Recursively compute the Fibonacci number F(n), where F(0) = 0, F(1) = 1.

    This will use the linear-time recursive algorithm with memoization, in
    which subproblems' results are cached and each call checks the cache before
    proceeding with a computation.

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
    Recursively compute the Fibonacci number F(n), where F(0) = 0, F(1) = 1.

    This will use the linear-time recursive algorithm with memoization, in
    which subproblems' results are cached and each call checks the cache before
    proceeding with a computation.

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
    Recursively compute the Fibonacci number F(n), where F(0) = 0, F(1) = 1.

    This will use the linear-time recursive algorithm with memoization, in
    which subproblems' results are cached and each call checks the cache before
    proceeding with a computation.

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
    >>> fibonacci_cached_3(500)
    139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
    """
    cache = {}
    
    if n == 0 or n == 1: 
        cache[n] = n
        return n 

    def helper(k):
        if k not in cache:
            cache[k] = helper(k - 1) + helper(k - 2)
        
        return cache[k]

    return helper(n)


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
