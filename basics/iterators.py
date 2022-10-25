#!/usr/bin/env python

"""
Concepts for iterators, revisited.

This module could theoretically be used to introduce the fundamentals of
iterators and generators, but it is NOT meant for that. Explanations target
readers who already know what generator functions, generator objects, and
iterators are. These are reviewed at a fast pace, without definitions, using
facilities from the inspect and collections.abc modules novices may not know.

Besides review, the primary purpose of this module is to present the __iter__
and __next__ special methods that the iter and next builtins use behind the
scenes. This reveals the nature of generator objects as state machines, and
shows why it is sometimes, but not always, okay for an attempt to construct an
iterable object to give an already-existing object, yet an attempt to construct
an iterator (generator or otherwise) must always give a newly created object.

On generators, see also the modules gencomp1.py and gencomp2.py, and the
notebooks gencomp1.ipynb, gencomp2.ipynb, and gencomp3.ipynb. Some techniques
appear in functions.py. On customizing object construction, see classes3.ipynb.
"""


def gen_rgb():
    """
    Yield the words "red", "green", and "blue", in that order.

    >>> from inspect import isfunction, isgeneratorfunction, isgenerator
    >>> from inspect import getgeneratorstate
    >>> from collections.abc import Iterable, Iterator

    A generator function is a factory for a generator object. The generator
    object itself is an iterator (it is also called a "generator iterator").
    The factory is not itself an iterator, nor is it otherwise iterable.

    >>> isfunction(gen_rgb), isgeneratorfunction(gen_rgb), isgenerator(gen_rgb)
    (True, True, False)
    >>> isinstance(gen_rgb, Iterable), isinstance(gen_rgb, Iterator)
    (False, False)

    >>> list(gen_rgb)
    Traceback (most recent call last):
      ...
    TypeError: 'function' object is not iterable

    Calling it returns a generator object, which is an iterator, thus iterable:

    >>> it = gen_rgb()
    >>> isfunction(it), isgeneratorfunction(it), isgenerator(it)
    (False, False, True)
    >>> isinstance(it, Iterable), isinstance(it, Iterator)
    (True, True)

    >>> list(it)
    ['red', 'green', 'blue']

    Iterators are exhausted by iteration:

    >>> list(it)
    []

    Calling iter on an iterator gives an equivalent iterator, which is almost
    always (and for generator objects, always) the very same iterator object:

    >>> it = gen_rgb()
    >>> iter(it) is it
    True

    Since iterators are exhausted by iteration, calling an iterator factory
    must always return a new iterator object. Equality is reference-based.

    >>> it2 = gen_rgb()
    >>> it is it2, it == it2
    (False, False)

    Each generator object created by a generator function separately executes
    the code in the function body, with its own instruction pointer and local
    variables. Before the first call to next, it has not even entered the code:

    >>> getgeneratorstate(it)
    'GEN_CREATED'

    The first call to next changes its state from GEN_CREATED to GEN_RUNNING,
    but its state is GEN_SUSPENDED after it yields, which is what we see:

    >>> next(it), getgeneratorstate(it)
    ('red', 'GEN_SUSPENDED')

    The full state of the generator object has more to it than just what
    inspect.getgeneratorstate returns. It knows where to resume.

    >>> next(it), getgeneratorstate(it), next(it), getgeneratorstate(it)
    ('green', 'GEN_SUSPENDED', 'blue', 'GEN_SUSPENDED')

    If the code returns instead of yielding, StopIteration is raised, and the
    generator state changes to GEN_CLOSE:

    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> getgeneratorstate(it), list(it), list(it)
    ('GEN_CLOSED', [], [])

    None of this affects it2, because that is a separate generator object:

    >>> getgeneratorstate(it2), next(it2), getgeneratorstate(it2)
    ('GEN_CREATED', 'red', 'GEN_SUSPENDED')

    Unlike most iterators, generator objects have a close method, which takes
    them to the GEN_CLOSED state. This skips over the remaining two elements:

    >>> it2.close()
    >>> getgeneratorstate(it2), list(it2), list(it2)
    ('GEN_CLOSED', [], [])

    Closing a suspended generator raises GeneratorExit in it, so any context
    managers are exited and any finally blocks are run. See gencomp3.ipynb.
    """
    yield 'red'
    yield 'green'
    yield 'blue'


if __name__ == '__main__':
    import doctest
    doctest.testmod()
