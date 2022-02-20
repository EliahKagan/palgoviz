"""Some basic decorators."""

import functools
import itertools

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
    """
    Decorator that memoizes a naive implementation of an algorithm.

    >>> @memoize
    ... def f(n):
    ...     print(n)
    ...     return n**2
    >>> f(2)
    2
    4
    >>> f(3)
    3
    9
    >>> f(2)
    4
    >>> f(3)
    9
    >>> @memoize
    ... def g(n):
    ...     print(n)
    ...     return n**3
    >>> g(2)
    2
    8
    >>> f(2)
    4
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(arg):
        if arg not in cache:
            cache[arg] = func(arg)
        return cache[arg]

    return wrapper


def int_fn(func):
    """
    Decorator that type-checks a unary function from int to int.

    Decorating a unary function definition with @int_fn causes the function to
    raise an exception if it is called with an argument that is not an int or
    if it returns a value that is not an int.

    >>> @int_fn
    ... def f(n):
    ...     print(f'f({n!r})')
    ...     return n + 1
    >>> f(1)
    f(1)
    2
    >>> f(False)
    f(False)
    1
    >>> f(1.1)
    Traceback (most recent call last):
      ...
    TypeError: f must be called with int, got float
    >>> @int_fn
    ... def g(n):
    ...     return n / 2
    >>> g(4)
    Traceback (most recent call last):
      ...
    TypeError: g must return an int, returned float
    >>> g(5)
    Traceback (most recent call last):
      ...
    TypeError: g must return an int, returned float
    """
    @functools.wraps(func)
    def wrapper(arg):
        if not isinstance(arg, int):
            raise TypeError(f'{func.__name__} must be called with int,'
                            f' got {type(arg).__name__}')
        result = func(arg)
        if not isinstance(result, int):
            raise TypeError(f'{func.__name__} must return an int,'
                            f' returned {type(result).__name__}')
        return result

    return wrapper


def count_calls(func):
    """
    Decorator like peek_arg, but that also counts calls to the function.

    >>> @count_calls
    ... def square(n): return n**2
    >>> result = square(3)
    square(3), call 1
    >>> result
    9
    >>> @count_calls
    ... def hello(name): print(f'Hello, {name}!')
    >>> hello('Bob')
    hello('Bob'), call 1
    Hello, Bob!
    >>> square(4)
    square(4), call 2
    16
    >>> hello('Bob')
    hello('Bob'), call 2
    Hello, Bob!
    >>> hello('Mary')
    hello('Mary'), call 3
    Hello, Mary!
    """
    counter = itertools.count(1)

    @functools.wraps(func)
    def wrapper(arg):
        print(f'{func.__name__}({arg!r}), call {next(counter)}')
        return func(arg)

    return wrapper


def convert_arg(converter):
    """
    Parametrized decorator to convert data going into a unary function.

    >>> @convert_arg(int)
    ... def square(n):
    ...     return n**2
    >>> square(3)
    9
    >>> square('4')
    16
    >>> square(5.1)
    25
    >>> @convert_arg(len)  # The converter can itself be any unary function.
    ... def mask(similar):
    ...     return '-' * similar
    >>> mask('hello')
    '-----'
    >>> @convert_arg(lambda s: s + 'ab')
    ... @convert_arg(str.upper)
    ... def munge1(text):
    ...     return text * 2
    >>> munge1('pqr')  # Outer converter appends, inner converter upcases.
    'PQRABPQRAB'
    >>> @convert_arg(str.upper)
    ... @convert_arg(lambda s: s + 'ab')
    ... def munge2(text):
    ...     return text * 2
    >>> munge2('pqr')  # Outer convert upcases, inner converter appends.
    'PQRabPQRab'
    """
    ...  # FIXME: Implement this.


def convert_return(converter):
    """
    Parametrized decorator to convert data coming out of a unary function.

    >>> @convert_return(list)
    ... def digits_lowtohigh(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_lowtohigh(4294967295)
    [5, 9, 2, 7, 6, 9, 4, 9, 2, 4]

    >>> @convert_return(lambda xs: xs[::-1])  # OK, xs will be a list.
    ... @convert_return(list)
    ... def digits_hightolow(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_hightolow(4294967295)
    [4, 2, 9, 4, 9, 6, 7, 2, 9, 5]

    >>> @convert_return(list)
    ... @convert_return(lambda xs: xs[::-1])  # NOT OK, xs will be a generator.
    ... def digits_hightolow(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_hightolow(4294967295)
    Traceback (most recent call last):
      ...
    TypeError: 'generator' object is not subscriptable

    >>> @convert_arg(int)                     # OK.
    ... @convert_return(lambda a: a[::-1])
    ... @convert_return(list)
    ... def digits_hightolow(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_hightolow(4294967295.3)
    [4, 2, 9, 4, 9, 6, 7, 2, 9, 5]

    >>> @convert_return(lambda a: a[::-1])
    ... @convert_return(list)
    ... @convert_arg(int)                     # OK.
    ... def digits_hightolow(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_hightolow(4294967295.3)
    [4, 2, 9, 4, 9, 6, 7, 2, 9, 5]

    >>> @convert_return(lambda a: a[::-1])
    ... @convert_arg(int)                     # Weird, but OK.
    ... @convert_return(list)
    ... def digits_hightolow(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_hightolow(4294967295.3)
    [4, 2, 9, 4, 9, 6, 7, 2, 9, 5]
    """
    ...  # FIXME: Implement this.
