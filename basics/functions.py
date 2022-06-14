#!/usr/bin/env python

"""
Examples demonstrating language features for functions.

This is a "bikeshed" file containing a handful of examples/exercises that don't
fit well elsewhere.

See also functions.ipynb, scopes.ipynb, and scopes.py.

Most material on higher-order functions is in composers.py or decorators.py.

TODO: Either move these functions to other modules or better explain what this
      module should and shouldn't contain.
"""

import contextlib
import itertools
from decorators import peek_return

from fibonacci import fib


def make_counter(start=0):
    """
    Create and return a function that returns successive integers on each call.

    This implementation never assigns to a variable that already exists.

    >>> f = make_counter()
    >>> [f(), f()]
    [0, 1]
    >>> g = make_counter()
    >>> [f(), g(), f(), g(), g()]
    [2, 0, 3, 1, 2]
    >>> h = make_counter(10)
    >>> [h(), f(), g(), h(), g(), h(), h(), g(), g(), f(), h()]
    [10, 4, 3, 11, 4, 12, 13, 5, 6, 5, 14]
    """
    it = itertools.count(start)
    return lambda: next(it)


def make_counter_alt(start=0):
    """
    Create and return a function that returns successive integers on each call.

    This implementation does not involve iterators in any way.

    >>> f = make_counter_alt()
    >>> [f(), f()]
    [0, 1]
    >>> g = make_counter_alt()
    >>> [f(), g(), f(), g(), g()]
    [2, 0, 3, 1, 2]
    >>> h = make_counter_alt(10)
    >>> [h(), f(), g(), h(), g(), h(), h(), g(), g(), f(), h()]
    [10, 4, 3, 11, 4, 12, 13, 5, 6, 5, 14]
    """
    def counter():
        nonlocal start
        current = start
        start += 1
        return current

    return counter


def make_next_fibonacci():
    """
    Create and return a function that returns successive Fibonacci numbers on
    each call.

    This implementation is simple, using an existing function in the project.

    >>> f = make_next_fibonacci()
    >>> [f() for _ in range(5)]
    [0, 1, 1, 2, 3]
    >>> g = make_next_fibonacci()
    >>> [x for _ in range(5) for x in (g(), f())]
    [0, 5, 1, 8, 1, 13, 2, 21, 3, 34]
    >>> [f(), f(), g()]
    [55, 89, 5]
    """
    it = fib()
    return lambda: next(it)


def make_next_fibonacci_alt():
    """
    Create and return a function that returns successive Fibonacci numbers on
    each call.

    This implementation is self-contained: it does not use anything defined
    outside, not even builtins. It also does not involve iterators in any way.

    >>> f = make_next_fibonacci_alt()
    >>> [f() for _ in range(5)]
    [0, 1, 1, 2, 3]
    >>> g = make_next_fibonacci_alt()
    >>> [x for _ in range(5) for x in (g(), f())]
    [0, 5, 1, 8, 1, 13, 2, 21, 3, 34]
    >>> [f(), f(), g()]
    [55, 89, 5]
    """
    a = 0
    b = 1

    def next_fib():
        nonlocal a, b
        ret = a
        a, b = b, a + b
        return ret

    return next_fib


def as_func(iterable):
    """
    Given an iterable, return a function that steps through it on each call.

    >>> f = as_func([10, 20, 30])
    >>> f()
    10
    >>> f()
    20
    >>> g = as_func(x**2 for x in itertools.count(2))
    >>> f()
    30
    >>> g()
    4
    >>> f()
    Traceback (most recent call last):
      ...
    StopIteration
    >>> g()
    9
    >>> g()
    16
    """
    it = iter(iterable)
    return lambda: next(it)


def as_func_limited(iterable, end_sentinel):
    """
    Return a function to step through an iterable or return a sentinel if done.

    Given an iterable, this returns a function that steps through it on each
    call, like as_func (above). But if the iterable has been exhausted, no
    exception is raised. Instead, end_sentinel is returned.

    >>> f = as_func_limited([10, 20], 'END')
    >>> f()
    10
    >>> f()
    20
    >>> f()
    'END'
    >>> f()
    'END'
    """
    it = iter(iterable)
    return lambda: next(it, end_sentinel)


def as_func_limited_alt(iterable, end_sentinel):
    """
    Return a function to step through an iterable or return a sentinel if done.

    This is an alternative implementation of as_func_limited. One
    implementation contains explicit try-except logic; the other does not.

    >>> f = as_func_limited_alt([10, 20], 'END')
    >>> f()
    10
    >>> f()
    20
    >>> f()
    'END'
    >>> f()
    'END'
    """
    it = iter(iterable)

    def get_next():
        try:
            return next(it)
        except StopIteration:
            return end_sentinel

    return get_next


def as_iterator_limited(func, end_sentinel):
    """
    Given a parameterless function, return an iterator that calls it until
    end_sentinel is reached.

    >>> it = as_iterator_limited(make_counter_alt(), 2000)
    >>> list(it) == list(range(2000))
    True
    >>> list(as_iterator_limited(make_next_fibonacci_alt(), 89))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    """
    return iter(func, end_sentinel)


def as_iterator_limited_alt(func, end_sentinel):
    """
    Given a parameterless function, return an iterator that calls it until
    end_sentinel is reached.

    This is an alternative implementation of as_iterator_limited. One
    implementation uses the iter builtin; the other does not.

    >>> it = as_iterator_limited_alt(make_counter_alt(), 2000)
    >>> list(it) == list(range(2000))
    True
    >>> list(as_iterator_limited_alt(make_next_fibonacci_alt(), 89))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    """
    while True:
        result = func()
        if result == end_sentinel:
            return
        yield result


def as_iterator(func):
    """
    Given a parameterless function, return an iterator that repeatedly calls
    it.

    >>> it = itertools.islice(as_iterator(make_counter_alt()), 2000)
    >>> list(it) == list(range(2000))
    True
    >>> list(itertools.islice(as_iterator(make_next_fibonacci_alt()), 11))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    """
    return iter(func, object())


def as_iterator_alt(func):
    """
    Given a parameterless function, return an iterator that repeatedly calls
    it.

    This is an alternative implementation of as_iterator. One implementation
    uses the iter builtin; the other does not.

    >>> it = itertools.islice(as_iterator_alt(make_counter_alt()), 2000)
    >>> list(it) == list(range(2000))
    True
    >>> list(itertools.islice(as_iterator_alt(make_next_fibonacci_alt()), 11))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    """
    while True:
        yield func()


def count_tree_nodes(root):
    """
    Recursively count nodes in a tuple structure.

    Empty tuples and non-tuples are leaves. Other objects are internal nodes.
    The structure is treated as a tree: objects reached in more than one way
    are counted multiple times. No memoization is performed.

    This is a simple recursive implementation. No helper function is used.

    >>> count_tree_nodes('a parrot')
    1
    >>> count_tree_nodes(())
    1
    >>> a = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
    >>> count_tree_nodes(a)
    22
    >>> count_tree_nodes([a])
    1
    >>> from fibonacci import fib_nest
    >>> [count_tree_nodes(fib_nest(k)) for k in range(17)]
    [1, 1, 3, 5, 9, 15, 25, 41, 67, 109, 177, 287, 465, 753, 1219, 1973, 3193]
    """
    if not isinstance(root, tuple):
        return 1

    return sum(count_tree_nodes(element) for element in root) + 1


def count_tree_nodes_alt(root):
    """
    Recursively count nodes in a tuple structure.

    Empty tuples and non-tuples are leaves. Other objects are internal nodes.
    The structure is treated as a tree: objects reached in more than one way
    are counted multiple times. No memoization is performed.

    This alternative implementation defines and calls a recursive helper
    function that does not return a value (really, it always returns None).
    No other callables, besides the helper and maybe builtins, are ever used.
    count_tree_nodes_alt never calls itself, nor does the helper ever call it.

    >>> count_tree_nodes_alt('a parrot')
    1
    >>> count_tree_nodes_alt(())
    1
    >>> a = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
    >>> count_tree_nodes_alt(a)
    22
    >>> count_tree_nodes_alt([a])
    1
    >>> from fibonacci import fib_nest
    >>> [count_tree_nodes_alt(fib_nest(k)) for k in range(17)]
    [1, 1, 3, 5, 9, 15, 25, 41, 67, 109, 177, 287, 465, 753, 1219, 1973, 3193]
    """
    count = 0

    def count_nodes(root):
        nonlocal count
        count +=1
        if not isinstance(root, tuple):
            return
        for element in root:
            count_nodes(element)

    count_nodes(root)
    return count


def count_tree_nodes_instrumented(root):
    """
    Call count_tree_nodes as if it were decorated with @decorators.peek_return.

    No logic from count_tree_nodes is reproduced. Subsequent calls to it do not
    have the modified behavior even if a prior call to it through this function
    raised an exception. But concurrent calls--like if it's called on another
    thread before a call to it through this function returns--need not be safe.

    Likewise, no logic from @peek_return is reproduced. If its behavior were to
    change--for example by using a different output format or even giving it by
    an entirely different means, such as posting it to a network server--then
    tests would need to change, but this function's implementation would not.

    >>> from recursion import make_deep_tuple
    >>> count_tree_nodes_instrumented(make_deep_tuple(2))
    count_tree_nodes(()) -> 1
    count_tree_nodes(((),)) -> 2
    count_tree_nodes((((),),)) -> 3
    3
    >>> count_tree_nodes(make_deep_tuple(3))
    4
    >>> try:
    ...     count_tree_nodes_instrumented(make_deep_tuple(5000))
    ... except RecursionError:
    ...     print('Got RecursionError.')
    ...     a = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
    ...     print(count_tree_nodes(a))
    Got RecursionError.
    22
    >>> from fibonacci import fib_nest
    >>> count_tree_nodes_instrumented(fib_nest(3))
    count_tree_nodes(1) -> 1
    count_tree_nodes(0) -> 1
    count_tree_nodes(1) -> 1
    count_tree_nodes((0, 1)) -> 3
    count_tree_nodes((1, (0, 1))) -> 5
    5
    """
    global count_tree_nodes
    non_decorated = count_tree_nodes
    count_tree_nodes = peek_return(count_tree_nodes)
    try:
        return count_tree_nodes(root)
    finally:
        count_tree_nodes = non_decorated


def _get_dict_attributes(obj):
    """Get an object's instance dictionary or, if absent, an empty mapping."""
    try:
        return obj.__dict__
    except AttributeError:
        return {}


def report_attributes(func):
    """
    Given a function (not other callables), report its non-metadata attributes.

    It is the caller's responsibility to ensure func is a function. Although
    bound methods are sometimes regarded to be functions, they are not allowed
    here. (Classes and callable instances are only ever informally regarded as
    functions, and are likewise not allowed.) You don't have to check for this.

    >>> report_attributes(lambda x: x**2)
    No non-metadata attributes.
    >>> def square(x): return x**2
    >>> square.foo = 42
    >>> square.bar = 'seventy-six'
    >>> report_attributes(square)
    square.foo = 42
    square.bar = 'seventy-six'
    >>> report_attributes(len)
    No non-metadata attributes.
    >>> def greet(value): print(greet.fmt.format(value))
    >>> greet.fmt = 'Hello, {}!'
    >>> report_attributes(greet)
    greet.fmt = 'Hello, {}!'
    """
    attributes = _get_dict_attributes(func)

    if not attributes:
        print('No non-metadata attributes.')
        return

    for key, value in attributes.items():
        print(f'{func.__name__}.{key} = {value!r}')


def as_closeable_func(iterable):
    """
    Return a function to step through an iterable, exposing close() if present.

    Given an iterable, this returns a function that steps through it on each
    call. If and only if the iterable's iterator is a generator or otherwise
    has a close method, the returned function also has a close "method." (It
    won't be a true method, since it won't be a member of the function's type,
    but it can be called like a method. Likewise, if close can be called on the
    input iterator, but it is not technically a method, still do support it.)

    This is like as_func (above), but with support for closing.

    >>> f = as_closeable_func(itertools.count(1))
    >>> [f() for _ in range(5)]
    [1, 2, 3, 4, 5]
    >>> hasattr(f, 'close')
    False
    >>> g = as_closeable_func(i for i in itertools.count(1))
    >>> [g() for _ in range(5)]
    [1, 2, 3, 4, 5]
    >>> g.close()
    >>> g()
    Traceback (most recent call last):
      ...
    StopIteration
    >>> h = as_closeable_func([10, 20, 30, 40, 50])
    >>> hasattr(h, 'close')
    False
    >>> list(as_iterator(h))
    [10, 20, 30, 40, 50]
    """
    it = iter(iterable)

    def get_next():
        return next(it)

    with contextlib.suppress(AttributeError):
        get_next.close = it.close

    return get_next


def as_closeable_func_limited(iterable, end_sentinel):
    """
    Return a function to step through an iterable or return a sentinel if done,
    exposing close() if present.

    Given an iterable, this returns a function that steps through it on each
    call, returning end_sentinel instead if the iterable has been exhausted,
    like as_func_limited and as_func_limited_alt.

    But if (and only if) the iterable's iterator supports closing, the returned
    function also has a close "method," just as in as_closeable_func.

    >>> f = as_closeable_func_limited(range(6), 11)
    >>> [f() for _ in range(9)]
    [0, 1, 2, 3, 4, 5, 11, 11, 11]
    >>> hasattr(f, 'close')
    False
    >>> g = as_closeable_func_limited((i for i in range(6)), 11)
    >>> a = [g() for _ in range(3)]
    >>> g.close()
    >>> a + [g() for _ in range(6)]
    [0, 1, 2, 11, 11, 11, 11, 11, 11]
    """
    it = iter(iterable)

    def get_next():
        return next(it, end_sentinel)

    with contextlib.suppress(AttributeError):
        get_next.close = it.close

    return get_next


def as_closeable_iterator_limited(func, end_sentinel):
    """
    Given a parameterless callable, return a generator that calls it until
    end_sentinel is reached, exposing close() if present.

    This is like as_iterator_limited and as_iterator_limited_alt. But the
    iterator it returns must be a generator object, and if func has a close
    method (or otherwise supports calling close on it like a method), then when
    the returned generator object is closed, this causes func to be closed.

    >>> a = [10, 20, 30, 40]
    >>> def f(): return a.pop()
    >>> f.close = lambda: print('Done.')
    >>> it1 = as_closeable_iterator_limited(f, 20)
    >>> list(it1)
    Done.
    [40, 30]
    >>> a
    [10]
    >>> it1.close()  # No output, the generator is already closed.
    >>> a = [10, 20, 30, 40]
    >>> it2 = as_closeable_iterator_limited(f, 20)
    >>> next(it2)
    40
    >>> it2.close()
    Done.
    >>> it3 = as_closeable_iterator_limited(f, 20)
    >>> it3.close()
    Done.
    """
    def generate():
        try:
            yield

            while (result := func()) != end_sentinel:
                yield result
        finally:
            try:
                close = func.close
            except AttributeError:
                pass
            else:
                close()

    it = generate()
    next(it)  # Enter the try block, so closing will run the finally block.
    return it


def as_closeable_iterator(func):
    """
    Given a parameterless callable, return an iterator that repeatedly calls
    it, exposing close() if present.

    This has the same relationship to as_iterator (and as_iterator_alt) that
    as_closeable_iterator_limited has to as_iterator_limited (and
    as_iterator_limited_alt). That is to say that this does the same thing as
    as_closeable_iterator_limited, except no sentinel value is recognized.

    >>> a = [10, 20, 30, 40]
    >>> b = []
    >>> def f(): return a.pop()
    >>> f.close = lambda: b.append('END')
    >>> it = as_closeable_iterator(f)
    >>> list(it)
    Traceback (most recent call last):
      ...
    IndexError: pop from empty list
    >>> b
    ['END']

    >>> def g():
    ...     try:
    ...         yield from (10, 20)
    ...     finally:
    ...         print('Done.')
    >>> it2 = as_closeable_iterator(as_closeable_func(g()))
    >>> next(it2)
    10
    >>> it2.close()
    Done.
    """
    return as_closeable_iterator_limited(func, object())


def func_filter(predicate, func, end_sentinel):
    """
    Like the filter builtin, but with functions instead of iterators.

    The func argument represents a series of items, returning the next item on
    each call. None of these items is equal to end_sentinel; func returns that
    value if called when exhausted. Return a function that likewise represents
    a series of items, consisting of those in func's series that satisfy the
    predicate. The returned function will delegate to func as needed. It will
    also return end_sentinel when exhausted.

    If the predicate argument is None instead of a unary function, the returned
    function represents the series of items in func's series that are truthy.

    This implementation does not involve iterators in any way.

    >>> a = [11, 22, 33, 44, 55, 66]
    >>> f = func_filter(lambda n: n % 2 == 0, a.pop, 33)
    >>> f()
    66
    >>> f()
    44
    >>> f()
    33
    >>> f()
    33
    >>> a
    [11, 22]
    """
    if predicate is None:
        predicate = lambda x: x

    done = False

    def get_next_satisfier():
        nonlocal done

        if done:
            return end_sentinel

        while (result := func()) != end_sentinel:
            if predicate(result):
                return result

        done = True
        return end_sentinel

    return get_next_satisfier


if __name__ == '__main__':
    import doctest
    doctest.testmod()
