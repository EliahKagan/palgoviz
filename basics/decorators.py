#!/usr/bin/env python

"""Some basic decorators."""

import functools
import itertools
from numbers import Number


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
        print(f'{func.__name__}({arg!r}) -> {result!r}')
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


def call_with(*args, **kwargs):
    """
    Parameterized decorator to call a function immediately with arguments.

    >>> @call_with('Dr. Evil', 'Albuquerque', exclaim=True)
    ... def welcome(name, place, exclaim=False):
    ...     punctuator = '!' if exclaim else '.'
    ...     print(f'Hello, {name}{punctuator} Welcome to {place}{punctuator}')
    Hello, Dr. Evil! Welcome to Albuquerque!
    >>> @call_with(*range(1, 11), verbose=True, padding=0)
    ... def print_sum(*addends, verbose, padding=1):
    ...     total = sum(addends)
    ...     if verbose:
    ...         pad = ' ' * padding
    ...         print(f'{pad}+{pad}'.join(map(str, addends)), '=', total)
    ...     else:
    ...         print(total)
    1+2+3+4+5+6+7+8+9+10 = 55
    >>> welcome('user', 'the internet')
    Hello, user. Welcome to the internet.
    >>> print_sum(-8, 2, 14, 9, verbose=False)
    17
    """
    def decorator(func):
        func(*args, **kwargs)
        return func

    return decorator


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


def peek_one(func):
    """
    Decorator that does the work of @peek_arg and @peek_return.

    Two for the price of one!

    >>> @peek_one
    ... def square(x): return x**2
    >>> result = square(3)
    square(3)
    square(3) -> 9
    """
    @functools.wraps(func)
    def wrapper(arg):
        print(f'{func.__name__}({arg!r})')
        result = func(arg)
        print(f'{func.__name__}({arg!r}) -> {result!r}')
        return result

    return wrapper


def peek(func):
    r"""
    Decorator to report calls with arbitrary arguments, and to report returns.

    This is like @peek_one (or @peek_arg and @peek_return), but the func need
    not be unary. Positional and keyword arguments are passed along to func.

    >>> @peek
    ... def square(x): return x**2
    >>> result = square(3)
    square(3)
    square(3) -> 9
    >>> @peek
    ... def proclaim(*args, **kwargs):
    ...     print('Good news', *args, **kwargs)
    >>> proclaim('Hello', 'world', sep=': ', end='!\n')
    proclaim('Hello', 'world', sep=': ', end='!\n')
    Good news: Hello: world!
    proclaim('Hello', 'world', sep=': ', end='!\n') -> None
    """
    @functools.wraps(func)
    def wrapper(*pargs, **kwargs):
        kvs = (f'{key}={value!r}' for key, value in kwargs.items())
        args_string = ', '.join(itertools.chain(map(repr, pargs), kvs))

        print(f'{func.__name__}({args_string})')
        result = func(*pargs, **kwargs)
        print(f'{func.__name__}({args_string}) -> {result!r}')
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


def memoize_by(key):
    """
    Parameterized decorator for caching using a key selector.

    This is like @memoize except the specified key selector function, key, maps
    arguments to hashable objects that are used as dictionary keys.

    NOTE: Argument values are NOT stored. For example, in @memoize_by(id),
    objects whose ids are taken are *not* kept alive by their ids being cached.
    Cached ids may become invalid by outliving the objects they came from.

    >>> @memoize_by(str.casefold)
    ... def length(text):
    ...     print(f'Computing the length of {text!r}.')
    ...     return len(text)
    >>> length('hello')
    Computing the length of 'hello'.
    5
    >>> length('Bye')
    Computing the length of 'Bye'.
    3
    >>> length('HELLO')
    5
    >>> length('bye')
    3
    """
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(arg):
            if key(arg) not in cache:
                cache[key(arg)] = func(arg)
            return cache[key(arg)]

        return wrapper

    return decorator


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
    def decorator(func):

        @functools.wraps(func)
        def wrapper(arg):
            return func(converter(arg))

        return wrapper

    return decorator


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

    >>> @convert_return(list)
    ... @convert_arg(int)
    ... @convert_return(lambda a: a[::-1])    # NOT OK, xs will be a generator.
    ... def digits_hightolow(positive_integer):
    ...     while positive_integer != 0:
    ...         yield positive_integer % 10
    ...         positive_integer //= 10
    >>> digits_hightolow(4294967295.3)
    Traceback (most recent call last):
      ...
    TypeError: 'generator' object is not subscriptable
    """
    def decorator(func):

        @functools.wraps(func)
        def wrapper(arg):
            return converter(func(arg))

        return wrapper

    return decorator


def auto_prime(func):
    """
    Decorator to automatically run returned generator up to the first yield.

    One use of this is to write generator functions contain their own fail-fast
    validation, without having to write a helper function each time.

    This is called "priming" the generator. It has some other use cases, too.

    >>> import collections, inspect
    >>> @auto_prime
    ... def alternate_ends(iterable, *, back_first=False):
    ...     pool = collections.deque(iterable)
    ...     yield  # The caller receives a generator primed to here.
    ...     if pool and back_first: yield pool.pop()
    ...     while pool:
    ...         yield pool.popleft()
    ...         if pool: yield pool.pop()

    >>> it = alternate_ends(range(1, 6))
    >>> inspect.getgeneratorstate(it)  # GEN_SUSPENDED instead of GEN_CREATED.
    'GEN_SUSPENDED'
    >>> list(it)
    [1, 5, 2, 4, 3]
    >>> list(alternate_ends(range(1, 6), back_first=True))
    [5, 1, 4, 2, 3]
    >>> alternate_ends(10 // i for i in range(3, -1, -1))  # Fails fast.
    Traceback (most recent call last):
      ...
    ZeroDivisionError: integer division or modulo by zero

    >>> @auto_prime
    ... def first_yield_non_none(values):
    ...     while values: yield values.pop()
    >>> a = [10, 20, 30]
    >>> first_yield_non_none(a)
    Traceback (most recent call last):
      ...
    TypeError: generator yielded non-None value when primed
    >>> a
    [10, 20]
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        if next(gen) is not None:
            raise TypeError('generator yielded non-None value when primed')
        return gen

    return wrapper


def dict_equality(cls):
    """
    Decorator to add instance dictionary based equality comparison and hashing.

    NOTE: This always adds hashing even if there are signs of mutability, such
    as writeable attributes whose names do not start with an underscore. But
    instances that themselves have attributes (stored in their instance
    dictionaries) whose values are non-hashable objects are non-hashable.

    >>> @dict_equality
    ... class Point:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...     def __repr__(self):
    ...         return f'{type(self).__name__}({self.x!r}, {self.y!r})'
    >>> Point(1, 2) == Point(1, 2) == Point(1.0, 2.0) != Point(2, 1)
    True
    >>> {Point(1, 2), Point(1, 2)}
    {Point(1, 2)}

    >>> @dict_equality
    ... class Weird:
    ...     __slots__ = ('a', 'b', '__dict__')
    ...     def __init__(self, a, b, c):
    ...         self.a = a
    ...         self.b = b
    ...         self.c = c
    >>> Weird(1, 2, 3) == Weird(4, 5, 3) != Weird(4, 5, 6)
    True

    >>> class Base:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    >>> @dict_equality
    ... class Derived(Base): pass
    >>> class MoreDerived(Derived): pass
    >>> Base(1, 2) == Derived(1, 2), Derived(1, 2) == Base(1, 2)
    (False, False)
    >>> Derived(1, 2) == MoreDerived(1, 2), MoreDerived(1, 2) == Derived(1, 2)
    (True, True)

    >>> @dict_equality
    ... class A: pass
    >>> @dict_equality
    ... class B: pass
    >>> class C: pass
    >>> A() == A(), A() == B(), B() == A(), A() == C(), C() == A()
    (True, False, False, False, False)
    """
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, type(self)):
            return self.__dict__ != other.__dict__
        return NotImplemented

    def __hash__(self):
        normalized = sorted(self.__dict__.items())
        flattened = itertools.chain.from_iterable(normalized)
        return hash(tuple(flattened))

    cls.__eq__ = __eq__
    cls.__ne__ = __ne__
    cls.__hash__ = __hash__
    return cls


def joining(sep=', ', *, use_repr=False, format_spec='', begin='', end=''):
    """
    Optionally parameterized decorator to join returned iterables into strings.

    The decorated function must return an iterable, but elements need not be
    strings. They are formatted with format_spec via the format builtin, unless
    use_repr is true; then their reprs are used and format_spec is ignored.

    This can be used as a decorator factory, passing zero or more arguments:

    >>> @joining(use_repr=True, begin='[', end=']')
    ... def f(n): return (ch * n for ch in 'ABC')
    >>> f(3)
    "['AAA', 'BBB', 'CCC']"
    >>> @joining('; ', format_spec='.2f')
    ... def g(a, b, *, delta=1):
    ...     while a < b:
    ...         yield a
    ...         a += delta
    >>> g(1.7, 6.4, delta=1.15)
    '1.70; 2.85; 4.00; 5.15; 6.30'

    When keeping all defaults, it can also be used directly as a decorator:

    >>> @joining
    ... def g(start, stop):
    ...     while start > stop:
    ...         yield start
    ...         start /= 2
    >>> g(7, 0.5)
    '7, 3.5, 1.75, 0.875'
    """
    if callable(sep):  # sep is actually the function, rather than a separator.
        return joining()(sep)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            to_str = repr if use_repr else lambda obj: format(obj, format_spec)
            joined = sep.join(map(to_str, func(*args, **kwargs)))
            return f'{begin}{joined}{end}'

        return wrapper

    return decorator


# !!FIXME: When removing implementation bodies, replace
#          "class linear_combinable:" with "def linear_combinable(func):".
class linear_combinable:
    """
    Decorator to wrap a function to support addition and scalar multiplication.

    Unary function definitions decorated with @linear_combinable support "+"
    and "-" among one another. They do not support "+" and "-" with functions
    not decorated @linear_combinable. They support "*" with instances of Number
    types, and "/" with nonzero instances of a Number type on the right. The
    results of all these operations themselves support these operations.

    The initial implementation should not use any helpers. But you may modify
    "def linear_combinable(func):" in any way that does not misinform the
    caller about proper usage (so no implementation-detail parameters).

    >>> @linear_combinable
    ... def f(x): 'Double a number.'; return x * 2
    >>> @linear_combinable
    ... def g(x): 'Square a number and subtract 1.'; return x**2 - 1
    >>> @linear_combinable
    ... def three(_): 'Return 3, no matter the argument.'; return 3

    >>> g(10)
    99
    >>> h = 3 * f - 2 * g + three
    >>> [h(x) for x in range(6)]
    [5, 9, 9, 5, -3, -15]
    >>> f + (lambda x: x**2)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +: '...' and 'function'

    >>> (2 * g / 2 * 2 / 2 * 2 / 2 * 2)(10)
    198.0
    >>> f / 0
    Traceback (most recent call last):
      ...
    ZeroDivisionError: second-order division by zero
    >>> 1 / f  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for /: 'int' and '...'
    >>> (2 * linear_combinable(str.upper) * 3 + f)('xyz')
    'XYZXYZXYZXYZXYZXYZxyzxyz'

    >>> for h in f, g, three:  # Check that metadata attributes are intact.
    ...     print([getattr(h, name) for name in functools.WRAPPER_ASSIGNMENTS])
    ['decorators', 'f', 'f', 'Double a number.', {}]
    ['decorators', 'g', 'g', 'Square a number and subtract 1.', {}]
    ['decorators', 'three', 'three', 'Return 3, no matter the argument.', {}]

    FIXME: Add a test to check that this works even when "*" isn't commutative.
    """

    def __init__(self, func):
        functools.wraps(func)(self)

    def __repr__(self):
        return f'{type(self).__name__}({self.__wrapped__!r})'

    def __call__(self, arg):
        return self.__wrapped__(arg)

    def __add__(self, right_addend):
        if not isinstance(right_addend, linear_combinable):
            return NotImplemented

        f = self.__wrapped__
        g = right_addend.__wrapped__
        return linear_combinable(lambda arg: f(arg) + g(arg))

    def __sub__(self, subtrahend):
        if not isinstance(subtrahend, linear_combinable):
            return NotImplemented

        f = self.__wrapped__
        g = subtrahend.__wrapped__
        return linear_combinable(lambda arg: f(arg) - g(arg))

    def __mul__(self, right_coefficient):
        if not isinstance(right_coefficient, Number):
            return NotImplemented

        f = self.__wrapped__
        return linear_combinable(lambda arg: f(arg) * right_coefficient)

    def __rmul__(self, left_coefficient):
        if not isinstance(left_coefficient, Number):
            return NotImplemented

        g = self.__wrapped__
        return linear_combinable(lambda arg: left_coefficient * g(arg))

    def __truediv__(self, divisor):
        if not isinstance(divisor, Number):
            return NotImplemented
        if divisor == 0:
            raise ZeroDivisionError('second-order division by zero')

        f = self.__wrapped__
        return linear_combinable(lambda arg: f(arg) / divisor)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
