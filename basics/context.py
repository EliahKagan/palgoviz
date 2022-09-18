#!/usr/bin/env python

"""Context managers."""

import functools


class Announce:
    """
    Context manager to announce starting and finishing a task, by name.

    >>> with Announce('Example Task') as ctx:
    ...     print(f'In task {ctx.name}.')
    Starting task Example Task.
    In task Example Task.
    Finished task Example Task.
    """

    __slots__ = ('_name', '_out')

    def __init__(self, name, *, out=None):
        """Create an announcer for a task of a specified name."""
        self._name = name
        self._out = out

    def __repr__(self):
        """Code-like representation for debugging."""
        if self._out is None:
            return f'{type(self).__name__}({self.name!r})'
        return f'{type(self).__name__}({self.name!r}, out={self._out!r})'

    def __enter__(self):
        """Announce the task is starting."""
        self._put(f'Starting task {self.name}.')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Announce the task has finished."""
        del exc_value, traceback

        if exc_type is None:
            self._put(f'Finished task {self.name}.')
        else:
            self._put(f'{exc_type.__name__} raised in task {self.name}.')

    @property
    def name(self):
        """The name of the task."""
        return self._name

    def _put(self, message):
        """Output a message to the appropriate output file/stream."""
        if self._out is None:
            print(message)
        else:
            print(message, file=self._out)


class Closing:
    """
    Context manager to call close. Like contextlib.closing.

    >>> with Closing(ch for ch in 'abcde') as gen:
    ...     print(next(gen), next(gen))
    a b
    >>> list(gen)
    []
    """

    __slots__ = ('_closeable_object',)

    def __init__(self, closeable_object):
        """Create a context manager that will close a particular object."""
        self._closeable_object = closeable_object

    def __repr__(self):
        """Representation of this object as Python code."""
        return f'{type(self).__name__}({self._closeable_object!r})'

    def __enter__(self):
        """Just return the closeable object."""
        return self._closeable_object

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the closeable object."""
        del exc_type, exc_value, traceback
        self._closeable_object.close()


class Suppress:
    """
    Context manager to swallow some exceptions. Like contextlib.suppress.

    >>> d = dict(s=20, q=10, v=30)
    >>> for ch in 'pqrstuvwx':
    ...     with Suppress(KeyError):
    ...         print(d[ch])
    10
    20
    30
    """

    __slots__ = ('_exception_types',)

    def __init__(self, *exception_types):
        """Create a context manager that "suppresses" given exception types."""
        self._exception_types = exception_types

    def __repr__(self):
        """Representation of this object, possibly runnable as Python code."""
        arguments = ', '.join(t.__name__ for t in self._exception_types)
        return f'{type(self).__name__}({arguments})'

    def __enter__(self):
        """Do nothing on entry to the context manager. (See __exit__.)"""

    def __exit__(self, exc_type, exc_value, traceback):
        """If an exception of an appropriate type was raised, suppress it."""
        del exc_value, traceback

        return (exc_type is not None
                and issubclass(exc_type, self._exception_types))


def _mp_repr(cls):
    """Decorator to define repr for MonkeyPatch and MonkeyPatchAlt."""
    def __repr__(self):
        """Representation of this object as Python code."""
        return (f'{type(self).__name__}({self._target!r}, {self._name!r}, '
                f'{self._new_value!r}, allow_absent={self._allow_absent!r})')

    cls.__repr__ = __repr__
    return cls


@_mp_repr
class MonkeyPatch:
    """
    Context manager and decorator to patch and unpatch an attribute.

    A MonkeyPatch instance may be used as a context manager:

    >>> import builtins, contextlib, math
    >>> with MonkeyPatch(builtins, 'len', lambda _: 42):
    ...     print(len([]))
    42
    >>> len([])
    0

    Or the instance may be used as a decorator:

    >>> @MonkeyPatch(builtins, 'len', lambda _: 42)
    ... def mean(*values):
    ...     return sum(values) / len(values)
    >>> mean(1, 3, 5)
    0.21428571428571427

    When used as a decorator, it is reentrant (and also preserves metadata):

    >>> two_digits = MonkeyPatch(math, 'pi', 3.14)
    >>> five_digits = MonkeyPatch(math, 'pi', 3.14159)
    >>> @two_digits
    ... def f(x):
    ...     '''f.'''
    ...     @five_digits
    ...     def g(y):
    ...         '''g.'''
    ...         @two_digits
    ...         def ff(p, q):
    ...             '''ff.'''
    ...             @five_digits
    ...             def gg(r, s):
    ...                 '''gg.'''
    ...                 print(math.pi, r, s, end=' ')
    ...                 raise ValueError
    ...             print(math.pi, gg.__name__, gg.__doc__, end=' ')
    ...             with contextlib.suppress(ValueError): gg(s=q+1, r=p+1)
    ...             print(math.pi, p, q, end=' ')
    ...         print(math.pi, ff.__name__, ff.__doc__, end=' ')
    ...         ff(y+1, q=y+2)
    ...         print(math.pi, y, end=' ')
    ...     print(math.pi, g.__name__, g.__doc__, end=' ')
    ...     g(x+1)
    ...     print(math.pi, x)
    ...     return x**2
    >>> print(math.pi, f.__name__, f.__doc__); print(f(4)); print(math.pi)
    3.141592653589793 f f.
    3.14 g g. 3.14159 ff ff. 3.14 gg gg. 3.14159 7 8 3.14 6 7 3.14159 5 3.14 4
    16
    3.141592653589793

    Hint: You might want to get it working just as a context manager first.
    """

    __slots__ = (
        '_target',
        '_name',
        '_new_value',
        '_allow_absent',
        '_has_old_value',
        '_old_value',
    )

    def __init__(self, target, name, new_value, *, allow_absent=False):
        """Create a context manager that will monkeypatch an attribute."""
        self._target = target
        self._name = name
        self._new_value = new_value
        self._allow_absent = allow_absent

    def __call__(self, func):
        """Wrap a function so each invocation patches and unpatches."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with type(self)(self._target, self._name, self._new_value,
                            allow_absent=self._allow_absent):
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        """Patch the attribute."""
        try:
            self._old_value = getattr(self._target, self._name)
        except AttributeError:
            if not self._allow_absent:
                raise
            self._has_old_value = False
        else:
            self._has_old_value = True

        setattr(self._target, self._name, self._new_value)

    def __exit__(self, exc_type, exc_value, traceback):
        """Unpatch the attribute."""
        del exc_type, exc_value, traceback

        if self._has_old_value:
            setattr(self._target, self._name, self._old_value)
        else:
            delattr(self._target, self._name)


@_mp_repr
class MonkeyPatchAlt:
    """
    Context manager and decorator to patch and unpatch an attribute.

    This is an alternative implementation of MonkeyPatch. The implementations
    differ in how they achieve reentrancy when used as decorators. One is also
    reentrant when used as a context manager (though we currently consider this
    an implementation detail that users should not rely on). As a result, it is
    more complicated overall, but the decorator-specific code is simpler. The
    other is reentrant only as a decorator, not as a context manager.

    >>> import builtins, contextlib, math
    >>> with MonkeyPatchAlt(builtins, 'len', lambda _: 42):
    ...     print(len([]))
    42
    >>> len([])
    0

    >>> @MonkeyPatchAlt(builtins, 'len', lambda _: 42)
    ... def mean(*values):
    ...     return sum(values) / len(values)
    >>> mean(1, 3, 5)
    0.21428571428571427

    >>> two_digits = MonkeyPatchAlt(math, 'pi', 3.14)
    >>> five_digits = MonkeyPatchAlt(math, 'pi', 3.14159)
    >>> @two_digits
    ... def f(x):
    ...     '''f.'''
    ...     @five_digits
    ...     def g(y):
    ...         '''g.'''
    ...         @two_digits
    ...         def ff(p, q):
    ...             '''ff.'''
    ...             @five_digits
    ...             def gg(r, s):
    ...                 '''gg.'''
    ...                 print(math.pi, r, s, end=' ')
    ...                 raise ValueError
    ...             print(math.pi, gg.__name__, gg.__doc__, end=' ')
    ...             with contextlib.suppress(ValueError): gg(s=q+1, r=p+1)
    ...             print(math.pi, p, q, end=' ')
    ...         print(math.pi, ff.__name__, ff.__doc__, end=' ')
    ...         ff(y+1, q=y+2)
    ...         print(math.pi, y, end=' ')
    ...     print(math.pi, g.__name__, g.__doc__, end=' ')
    ...     g(x+1)
    ...     print(math.pi, x)
    ...     return x**2
    >>> print(math.pi, f.__name__, f.__doc__); print(f(4)); print(math.pi)
    3.141592653589793 f f.
    3.14 g g. 3.14159 ff ff. 3.14 gg gg. 3.14159 7 8 3.14 6 7 3.14159 5 3.14 4
    16
    3.141592653589793
    """

    __slots__ = (
        '_target',
        '_name',
        '_new_value',
        '_allow_absent',
        '_history',
    )

    _absent = object()
    """Sentinel object representing the absence of an attribute value."""

    def __init__(self, target, name, new_value, *, allow_absent=False):
        """Create a context manager that will monkeypatch an attribute."""
        self._target = target
        self._name = name
        self._new_value = new_value
        self._allow_absent = allow_absent
        self._history = []

    def __call__(self, func):
        """Wrap a function so each invocation patches and unpatches."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        """Patch the attribute."""
        try:
            value = getattr(self._target, self._name)
        except AttributeError:
            if not self._allow_absent:
                raise
            self._history.append(self._absent)
        else:
            self._history.append(value)

        setattr(self._target, self._name, self._new_value)

    def __exit__(self, exc_type, exc_value, traceback):
        """Unpatch the attribute."""
        del exc_type, exc_value, traceback

        old_value = self._history.pop()

        if old_value is self._absent:
            delattr(self._target, self._name)
        else:
            setattr(self._target, self._name, old_value)


__all__ = [thing.__name__ for thing in (
    Announce,
    Closing,
    Suppress,
    MonkeyPatch,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
