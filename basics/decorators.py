"""Some basic decorators."""

import functools

from composers import compose2


def peek_arg(func):
    """
    Decorator wrapping a unary function and showing calls to it.

    This peeks at the argument passed when the function is called.
    It does not show the value returned.

    >>> @peek_arg
    ... def square(n): return n**2
    >>> result = square(3)
    square(3)
    >>> result
    9
    >>> @peek_arg
    ... def hello(name): print(f'Hello, {name}!')
    >>> hello('Bob')
    hello('Bob')
    Hello, Bob!
    """
    @functools.wraps(func)
    def wrapper(arg):
        print(f'{func.__name__}({arg!r})')
        return func(arg)

    return wrapper


def peek_return(func):
    """
    Decorator wrapping a unary function and showing its return values.

    This peeks at the value returned by the function. It does not print
    anything at the time the function is called.

    >>> @peek_return
    ... def square(x): return x**2
    >>> result = square(3)
    square(3) -> 9
    >>> result
    9
    >>> @peek_return
    ... def hello(name): print(f'Hello, {name}!')
    >>> hello('Bob')
    Hello, Bob!
    hello('Bob') -> None
    """
    @give_metadata_from(func)
    def wrapper(arg):
        result = func(arg)
        print(f'{func.__name__}({arg!r}) -> {result}')
        return result

    return wrapper


def call(func):
    """
    Decorator to call a parameterless function immediately.

    >>> @call
    ... def hi():
    ...     print('Hi, world!')
    Hi, world!
    >>> hi()
    Hi, world!
    """
    func()
    return func


def thrice(func):
    """
    Decorator to repeat a parameterless function three times (with no return).

    >>> @thrice
    ... def hello(): print('Hello, world!')
    >>> hello()
    Hello, world!
    Hello, world!
    Hello, world!
    >>> @thrice
    ... def answer(): return 42
    >>> answer()  # No output; the wrapped function always returns None.
    >>>
    """
    @functools.wraps(func)
    def wrapper():
        for _ in range(3):
            func()

    return wrapper


def repeat(count):
    """
    Parameterized decorator to repeat a function a given number of times.

    >>> @repeat(2)
    ... def bye():
    ...     print('Cya later!')
    >>> bye()
    Cya later!
    Cya later!
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper():
            for _ in range(count):
                func()

        return wrapper

    return decorator


def peek(func):
    """Decorator that does the work of peek arg and peek return. Two for the price of one!

    >>> @peek
    ... def square(x): return x**2
    >>> result = square(3)
    square(3)
    square(3) -> 9
    """
    @functools.wraps(func)
    def wrapper(arg):
        print(f'{func.__name__}({arg!r})')
        result = func(arg)
        print(f'{func.__name__}({arg!r}) -> {result}')
        return result

    return wrapper


def give_metadata_from(wrapped):
    """Parameterized decorater to give a function's metadata to a wrapper."""
    def decorator(wrapper):
        wrapper.__name__ = wrapped.__name__
        wrapper.__module__ = wrapped.__module__
        wrapper.__qualname__ = wrapped.__qualname__
        wrapper.__doc__ = wrapped.__doc__
        wrapper.__annotations__ = wrapped.__annotations__
        return wrapper

    return decorator


def memoize(func):
    @functools.wraps(func)
    def wrapper(arg):
        cache = {}
        if arg not in cache:
            cache[arg] = func(arg)
        return cache[arg]
    return wrapper


# Notes that I used to reason out what memoize does to wrapped.

# def fibonacci_wrapped(n):
#     """
#     Memoized recursive Fibonacci algorithm. Fourth way.

#     This computes the Fibonacci number F(n) in linear time.

#     >>> fibonacci(0)
#     0
#     >>> fibonacci(1)
#     1
#     >>> fibonacci(2)
#     1
#     >>> fibonacci(3)
#     2
#     >>> fibonacci(10)
#     55
#     >>> fibonacci(500)
#     139423224561697880139724382870407283950070256587697307264108962948325571622863290691557658876222521294125
#     """
#     def helper(x):
#         if x == 0:
#             return 0
#         if x == 1:
#             return 1
#         return fibonacci_wrapped(x - 1) + fibonacci_wrapped(x - 2)
#
#     cache = {}
#     if n not in cache:
#         cache[n] = helper(n)
#     return cache[n]

