#!/usr/bin/env python

"""
Some basic, and not so basic, decorators.

Caching decorators like @memoize and @memoize_by are in the caching module.
"""

import functools
import itertools
import numbers


def identity_function(arg):
    """Return the argument unchanged."""
    return arg


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
    """  # r makes this a raw string literal.
    @functools.wraps(func)
    def wrapper(*pargs, **kwargs):
        kvs = (f'{key}={value!r}' for key, value in kwargs.items())
        args_string = ', '.join(itertools.chain(map(repr, pargs), kvs))

        print(f'{func.__name__}({args_string})')
        result = func(*pargs, **kwargs)
        print(f'{func.__name__}({args_string}) -> {result!r}')
        return result

    return wrapper


def give_metadata_from(wrapped, *, expose=False):
    """
    Parameterized decorator to give a function's metadata to a wrapper.

    This copies the metadata attributes @functools.wraps copies by default, but
    they are not customizable, and AttributeError is raised if any are absent
    on the wrapped function (or class). No other attributes are copied, but if
    expose=True then __wrapped__ is also set on the wrapper, giving access to
    the wrapped function.

    __wrapped__ is a dunder, but this should be okay because it is not a new
    dunder and is being used as documented in functools.update_wrapper:

    https://docs.python.org/3/library/functools.html#functools.update_wrapper

    >>> def f(): 'Wrapped docstring.'

    >>> @give_metadata_from(f)
    ... def g(): pass
    >>> g.__name__, g.__module__, g.__qualname__, g.__doc__, g.__annotations__
    ('f', 'decorators', 'f', 'Wrapped docstring.', {})
    >>> hasattr(g, '__wrapped__')
    False

    >>> @give_metadata_from(f, expose=True)
    ... def h(): pass
    >>> h.__name__, h.__module__, h.__qualname__, h.__doc__, h.__annotations__
    ('f', 'decorators', 'f', 'Wrapped docstring.', {})
    >>> h.__wrapped__ is f
    True

    @give_metadata_from supports no other customization. But it automatically
    supports one important case where @functools.wraps does need customization.
    When the wrapper is a class, its __dict__ attribute is a mappingproxy, so:

    >>> @functools.wraps(f)  # Will try to call C1.__dict__.update(f.__dict__).
    ... class C1: pass
    Traceback (most recent call last):
      ...
    AttributeError: 'mappingproxy' object has no attribute 'update'

    >>> @functools.wraps(f, updated=())  # Works, no C2.__dict__.update call.
    ... class C2: pass
    >>> C2.__name__
    'f'

    >>> @give_metadata_from(f)  # Never calls anything like C3.__dict__.update.
    ... class C3: pass
    >>> C3.__name__
    'f'
    """
    def decorator(wrapper):
        wrapper.__name__ = wrapped.__name__
        wrapper.__module__ = wrapped.__module__
        wrapper.__qualname__ = wrapped.__qualname__
        wrapper.__doc__ = wrapped.__doc__
        wrapper.__annotations__ = wrapped.__annotations__

        if expose:
            wrapper.__wrapped__ = wrapped

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
    Decorator to automatically run returned generators up to their first yield.

    One use of this is to write generator functions that contain their own
    fail-fast validation, without having to write a helper function each time.

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
    def wrapper(*pargs, **kwargs):
        generator = func(*pargs, **kwargs)
        if next(generator) is not None:
            raise TypeError('generator yielded non-None value when primed')
        return generator

    return wrapper


def assign_attributes(**assignments):
    """
    Parameterized decorator to assign attributes on a function or class.

    >>> @assign_attributes(__name__='affine', weight=10, bias=20)
    ... def f(x): return x * f.weight + f.bias
    >>> f.__name__, f.weight, f.bias, f(3.75)
    ('affine', 10, 20, 57.5)

    >>> @assign_attributes(__add__=lambda self, other: other,
    ...                    __radd__=lambda self, other: other)
    ... class UniversalAdditiveIdentity: __slots__ = ()
    >>> 3 + UniversalAdditiveIdentity(), [10, 20] + UniversalAdditiveIdentity()
    (3, [10, 20])
    >>> UniversalAdditiveIdentity() + 3, UniversalAdditiveIdentity() + [10, 20]
    (3, [10, 20])
    """
    def decorator(func_or_class):
        for key, value in assignments.items():
            setattr(func_or_class, key, value)
        return func_or_class

    return decorator


def suppressing(*exception_types, fallback_result=None):
    """
    Parameterized decorator to suppress and return on specific exception types.

    >>> @suppressing(TypeError, IndexError, fallback_result='FAIL!')
    ... def add_firsts(a, b, *, reverse=False):
    ...     return b[0] + a[0] if reverse else a[0] + b[0]

    >>> add_firsts('foo', 'bar'), add_firsts('foo', 'bar', reverse=True)
    ('fb', 'bf')
    >>> add_firsts('foo', 3), add_firsts('foo', 3, reverse=True)
    ('FAIL!', 'FAIL!')
    >>> add_firsts('', 'bar'), add_firsts('', 'bar', reverse=True)
    ('FAIL!', 'FAIL!')
    >>> add_firsts({}, 2)
    Traceback (most recent call last):
      ...
    KeyError: 0

    >>> suppressing(ValueError)(int)('2.5') is None
    True
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*pargs, **kwargs):
            try:
                return func(*pargs, **kwargs)
            except exception_types:
                return fallback_result

        return wrapper

    return decorator


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
    >>> x = A(); y = A(); x.p = 10; x.q = 20; y.q = 20; y.p = 10
    >>> x == y, hash(x) == hash(y)
    (True, True)
    """
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.__dict__ == other.__dict__

    cls.__eq__ = __eq__

    if cls.__ne__ is not object.__ne__:
        def __ne__(self, other):
            if not isinstance(other, type(self)):
                return NotImplemented
            return self.__dict__ != other.__dict__

        cls.__ne__ = __ne__

    def __hash__(self):
        return hash(frozenset(self.__dict__.items()))

    cls.__hash__ = __hash__

    return cls


def count_calls_in_attribute(optional_func=None, /, *, name='count'):
    """
    Optionally parameterized decorator to count calls in a function attribute.

    This can be used as a decorator factory, specifying the name to be used for
    the counter attribute:

    >>> @count_calls_in_attribute(name='veterancy')
    ... def do(verb, noun, direction, speed):
    ...     print(f'Got: {verb=}, {noun=}, {direction=}, {speed=}')
    >>> do.veterancy
    0
    >>> do('defuse', 'bomb', 'northwest', 'slow'); do.veterancy
    Got: verb='defuse', noun='bomb', direction='northwest', speed='slow'
    1
    >>> do('carry', 'microfilm', speed='fast', direction='east'); do.veterancy
    Got: verb='carry', noun='microfilm', direction='east', speed='fast'
    2
    >>> hasattr(do, 'count')  # Named counter and metadata attributes only.
    False

    The attribute name is optional, defaulting to "count":

    >>> @count_calls_in_attribute()  # Same as passing name='count'.
    ... def add_up(*nums): return sum(nums)
    >>> add_up.count, add_up(2, 7, 3), add_up(), add_up(4, 1), add_up.count
    (0, 12, 0, 5, 3)

    When keeping this default, it can also be used directly as a decorator:

    >>> @count_calls_in_attribute
    ... def add_up(*nums): return sum(nums)
    >>> add_up.count, add_up(2, 7, 3), add_up(), add_up(4, 1), add_up.count
    (0, 12, 0, 5, 3)

    Hint: You might want to get it working just as a decorator factory first.
    """
    if optional_func is not None:
        return count_calls_in_attribute(name=name)(optional_func)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*pargs, **kwargs):
            setattr(wrapper, name, getattr(wrapper, name) + 1)
            return func(*pargs, **kwargs)

        setattr(wrapper, name, 0)
        return wrapper

    return decorator


def _wrap_if_uncallable(value):
    return value if callable(value) else lambda *_args, **_kwargs: value


def wrap_uncallable_args(optional_func=None, /, *, kw=False):
    """
    Optionally parameterized decorator to convert non-callable arguments to
    constant functions.

    When a higher-order function expects its arguments to be callable, but you
    want to pass some non-callable values when you really mean functions that
    always return those values, this decorator lets you do that. See make_fmap
    below for an intuitive use. Its tests should pass once this is implemented.

    By default, only non-callable positional arguments are made into constant
    functions. But with kw=True, non-callable keyword arguments are also made
    into constant functions.

    Since functions and other callables may have side effects (including side
    effects that cause a different value to be returned on a later call with
    the same arguments), this must check callability without attempting calls.

    "Wrap" in "wrap_uncallable_args" refers to wrapping a value and returning
    it. This is subtly different from wrapping another function and calling it,
    which is the kind of wrapping more often relevant to decorators.

    wrap_uncallable_args can be used as a decorator factory, with kw=False:

    >>> @wrap_uncallable_args(kw=False)  # Same effect as with "()".
    ... def pass_args_through_1(*args, **kwargs): return args, kwargs
    >>> a, kw = pass_args_through_1(min, 42, f=max, g=76)
    >>> a[0](5, 7), a[0](7, 5), a[1](5, 7), a[1](7, 5), kw, a[1](0, x=4, w=6)
    (5, 5, 42, 42, {'f': <built-in function max>, 'g': 76}, 42)

    wrap_uncallable_args can be used as a decorator factory, with kw=True:

    >>> @wrap_uncallable_args(kw=True)  # kw=True has to be passed explicitly.
    ... def pass_args_through_2(*args, **kwargs): return args, kwargs
    >>> a, kw = pass_args_through_2(min, 42, f=max, g=76)
    >>> a[0](5, 7), a[0](7, 5), a[1](5, 7), a[1](7, 5)
    (5, 5, 42, 42)
    >>> kw['f'](5, 7), kw['f'](7, 5), kw['g'](5, 7), kw['g'](7, 5)
    (7, 7, 76, 76)
    >>> a[1](0, x=4, w=6), kw['g'](0, x=4, w=6)
    (42, 76)

    wrap_uncallable_args can also be used directly as a decorator, but only if
    you want the default of kw=False:

    >>> @wrap_uncallable_args  # Same effect here as with "()", too.
    ... def pass_args_through_3(*args, **kwargs): return args, kwargs
    >>> a, kw = pass_args_through_3(min, 42, f=max, g=76)
    >>> a[0](5, 7), a[0](7, 5), a[1](5, 7), a[1](7, 5), kw, a[1](0, x=4, w=6)
    (5, 5, 42, 42, {'f': <built-in function max>, 'g': 76}, 42)
    """
    if optional_func is not None:
        return wrap_uncallable_args(kw=kw)(optional_func)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args = map(_wrap_if_uncallable, args)

            if kw:
                kwargs = {name: _wrap_if_uncallable(value)
                          for name, value in kwargs.items()}

            return func(*args, **kwargs)

        return wrapper

    return decorator


def make_fmap(preimage, *, strict=False, collector=tuple):
    """
    Make a function that applies many functions to one argument, the preimage.

    This demonstrates an intuitive use of @wrap_uncallable_args. Here, the
    "functions" must be unary (even as @wrap_uncallable_args imposes no such
    restriction). But they may be any callables, not just actual functions.

    >>> class Squarer:
    ...     def __call__(self, x): return x**2

    >>> make_fmap(-7)(abs, Squarer(), 3, lambda x: 2**x, -5)
    (7, 49, 3, 0.0078125, -5)

    >>> make_fmap(-7, strict=True)(abs, Squarer(), 3, lambda x: 2**x, -5)
    Traceback (most recent call last):
      ...
    TypeError: 'int' object is not callable
    """
    if collector is None:
        collector = identity_function

    @(identity_function if strict else wrap_uncallable_args)
    def fmap(*functions):
        return collector(f(preimage) for f in functions)

    return fmap


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
    if callable(sep):  # In this case, sep is the function, not a separator.
        return joining()(sep)

    if not isinstance(sep, str):
        raise TypeError('separator must be a string')

    get_token = repr if use_repr else lambda value: format(value, format_spec)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tokens = map(get_token, func(*args, **kwargs))
            return f'{begin}{sep.join(tokens)}{end}'

        return wrapper

    return decorator


def repeat_collect(count=2):
    r"""
    Optionally parameterized decorator to repeat a function and return all
    results.

    This is like @repeat(), except (1) this can decorate any function of any
    signature, not just parameterless functions, (2) it returns a tuple of the
    results from each call, and (3) it can be used as a decorator factory or a
    plain decorator (in which case the default repetition count of 2 is used).

    It is not a goal to return information about combinations of successes and
    failures. If any of the repeated calls raises an exception, that exception
    is propagated, and any results of previous calls are discarded.

    >>> import math, io, itertools

    >>> indices = itertools.count(1)
    >>> @repeat_collect(3)
    ... def f(*, weight, bias):
    ...     print(f'Called {f.__name__}({weight=}, {bias=}).')
    ...     return next(indices) * weight + bias
    >>> f(weight=2, bias=3)
    Called f(weight=2, bias=3).
    Called f(weight=2, bias=3).
    Called f(weight=2, bias=3).
    (5, 7, 9)

    >>> sio = io.StringIO('foo\nbar\nbaz\n')
    >>> @repeat_collect
    ... def g(back, front):
    ...     return back(front(sio.readline().removesuffix('\n')))
    >>> g(str.capitalize, lambda s: s[1:])
    ('Oo', 'Ar')

    >>> repeat_collect(0)(math.cos)(math.pi)
    ()
    >>> repeat_collect(1)(math.cos)(math.pi)
    (-1.0,)
    >>> repeat_collect(2)(math.cos)(math.pi)
    (-1.0, -1.0)
    >>> repeat_collect()(math.cos)(math.pi)
    (-1.0, -1.0)
    >>> repeat_collect(math.cos)(math.pi)
    (-1.0, -1.0)
    """
    if callable(count):  # In this case, count is the function, not a count.
        return repeat_collect()(count)

    if not isinstance(count, int):
        raise TypeError('count must be an int')

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return tuple(func(*args, **kwargs) for _ in range(count))

        return wrapper

    return decorator


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
    >>> def sq(x): x**2
    >>> f + sq  # doctest: +ELLIPSIS
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

    >>> len({f, g, three, linear_combinable(sq), linear_combinable(sq)})
    4
    >>> for h in f, g, three:  # Check that metadata attributes are intact.
    ...     print([getattr(h, name) for name in functools.WRAPPER_ASSIGNMENTS])
    ['decorators', 'f', 'f', 'Double a number.', {}]
    ['decorators', 'g', 'g', 'Square a number and subtract 1.', {}]
    ['decorators', 'three', 'three', 'Return 3, no matter the argument.', {}]

    FIXME: Add a test to check that this works even when "*" isn't commutative.
    """

    def __init__(self, func):
        self._func = func
        functools.update_wrapper(self, func)  # Or: functools.wraps(func)(self)

    def __call__(self, x):
        return self.func(x)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.func == other.func

    def __hash__(self):
        return hash(self.func)

    def __add__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return linear_combinable(lambda x: self(x) + other(x))

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return linear_combinable(lambda x: self(x) - other(x))

    def __mul__(self, other):
        if not isinstance(other, numbers.Number):
            return NotImplemented

        return linear_combinable(lambda x: self(x) * other)

    def __rmul__(self, other):
        if not isinstance(other, numbers.Number):
            return NotImplemented

        return linear_combinable(lambda x: self(x) * other)

    def __truediv__(self, other):
        if not isinstance(other, numbers.Number):
            return NotImplemented

        if other == 0:
            raise ZeroDivisionError("second-order division by zero")

        return linear_combinable(lambda x: self(x) / other)

    @property
    def func(self):
        return self._func


__all__ = [thing.__name__ for thing in (
    identity_function,
    peek_arg,
    peek_return,
    call,
    call_with,
    thrice,
    repeat,
    peek_one,
    peek,
    give_metadata_from,
    int_fn,
    count_calls,
    convert_arg,
    convert_return,
    auto_prime,
    assign_attributes,
    suppressing,
    dict_equality,
    count_calls_in_attribute,
    wrap_uncallable_args,
    make_fmap,
    joining,
    repeat_collect,
    linear_combinable,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
