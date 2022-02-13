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
    def fib(k):
        if k - 2 == 0:
            a = 0
        elif k - 2 == 1:
            a = 1
        else:
            a = fib(k - 2)

        if k - 1 == 0:
            b = 0
        elif k - 1 == 1:
            b = 1
        else:
            b = fib(k - 1)

        return a + b

    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n)


def fibonacci_short_alr(n):
    """
    Compute the Fibonacci number F(n) with arm's recursion more compactly.

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
    def fib(k):
        a = k - 2 if k < 4 else fib(k - 2)  # k < 4 iff k - 2 < 2
        b = k - 1 if k < 3 else fib(k - 1)  # k < 3 iff k - 1 < 2
        return a + b

    return n if n < 2 else fib(n)


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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
