"""Some basic decorators."""


def peek_arg(func):
    """
    Return a wrapper for unary function that prints how it is called.

    >>> def square(n): return n**2
    >>> psquare = peek_arg(square)
    >>> result = psquare(3)
    square(3)
    >>> result
    9
    """

    def wrapper(n):
        print(f'{func.__name__}({n})')
        return func(n)

    return wrapper
