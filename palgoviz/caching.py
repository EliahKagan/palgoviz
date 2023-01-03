#!/usr/bin/env python

# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Caching decorators.

Most other decorators, not related to caching, are in decorators.py.
"""

__all__ = ['memoize', 'memoize_by']

import functools


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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
