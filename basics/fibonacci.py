#!/usr/bin/env python

"""
Fibonacci sequence - computation and analysis/visualization

See also the visualizations in subproblems.ipynb.

For the command-line Fibonacci numbers program that calls fib_n, see fib.py.
"""


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


# FIXME: Implement this, caching the results of each recursive call.
def fibonacci_better(n):
    """
    Recursively compute the Fibonacci number F(n), where F(0) = 0, F(1) = 1.

    This will use the linear-time recursive algorithm with memoization, in
    which subproblems' results are cached and each call checks the cache before
    proceeding with a computation.

    >>> fibonacci_better(0)
    0
    >>> fibonacci_better(1)
    1
    >>> fibonacci_better(2)
    1
    >>> fibonacci_better(3)
    2
    >>> fibonacci_better(10)
    55

    FIXME: Add a test case that times out with simple recursion.
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


# TODO: When we do unittest and pytest, translate these doctests and observe
#       how much clearer (and easier to get right) they are.
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
    >>> fib_n(1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> list(fib_n(True))  # OK, since bool is a subclass of int.
    [0]
    """
    if n < 0:
        raise ValueError(f"can't yield negatively many Fibonacci numbers")

    if not isinstance(n, int):
        raise TypeError('n must be an int')

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

    # FIXME: Add doctests.
    """
    a = 0
    b = 1
    yield a
    yield b 
    while True:
        a, b = b, a + b
        yield b



if __name__ == '__main__':
    import doctest
    doctest.testmod()
