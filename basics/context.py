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
        """Codelike representation for debugging."""
        if self._out is None:
            return f'{type(self).__name__}({self.name!r})'

        return f'{type(self).__name__}({self.name!r}, out={self._out!r})'

    def __enter__(self):
        """Announce the start of the task."""
        self._print(f'Starting task {self.name}.')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Announce that the task completed or raised an exception."""
        del exc_value, traceback

        if exc_type is None:
            self._print(f'Finished task {self.name}.')
        else:
            self._print(f'{exc_type.__name__} raised in task {self.name}.')

    @property
    def name(self):
        """Name of the task."""
        return self._name

    def _print(self, message):
        """Output a message to appropriate file/stream."""
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

    __slots__ = ('_obj',)

    def __init__(self, obj):
        """Create a context manager that will close an object."""
        self._obj = obj

    def __repr__(self):
        """Codelike representation for debugging."""
        return f'{type(self).__name__}({self._obj!r})'

    def __enter__(self):
        """Just return the object (that will be closed)."""
        return self._obj

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the object."""
        del exc_type, exc_value, traceback
        self._obj.close()


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

    __slots__ = ('_exc_types',)

    def __init__(self, *exc_types):
        """Create a context manager to suppress given exception types."""
        self._exc_types = exc_types

    def __repr__(self):
        """Representation as Python code."""
        type_names = ', '.join(e_type.__name__ for e_type in self._exc_types)
        return f'{type(self).__name__}({type_names})'

    def __enter__(self):
        """Do nothing."""
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """Suppress appropriate exception types."""
        del exc_value, traceback

        if exc_type is None:
            return False

        return issubclass(exc_type, self._exc_types)


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
        '_value',
        '_allow_absent',
        '_old_stack',
    )

    _absent = object()

    def __init__(self, target, name, value, *, allow_absent=False):
        """Create a context manager to patch and unpatch an attribute."""
        self._target = target
        self._name = name
        self._value = value
        self._allow_absent = allow_absent
        self._old_stack = []

    def __repr__(self):
        """Codelike representation for debugging."""
        return '{}({!r}, {!r}, {!r}, allow_absent={!r})'.format(
            type(self).__name__,
            self._target,
            self._name,
            self._value,
            self._allow_absent,
        )

    def __call__(self, func):
        """Wrap so each call patches and unpatches the attribute."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        """Patch the attribute."""
        try:
            old = getattr(self._target, self._name)
        except AttributeError:
            if not self._allow_absent:
                raise
            old = self._absent

        self._old_stack.append(old)
        setattr(self._target, self._name, self._value)

    def __exit__(self, exc_type, exc_value, traceback):
        """Unpatch the attribute."""
        del exc_type, exc_value, traceback

        old = self._old_stack.pop()

        if old is self._absent:
            delattr(self._target, self._name)
        else:
            setattr(self._target, self._name, old)


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
        '_value',
        '_allow_absent',
        '_old',
        '_absent',
    )

    def __init__(self, target, name, value, *, allow_absent=False):
        """Create a context manager to patch and unpatch an attribute."""
        self._target = target
        self._name = name
        self._value = value
        self._allow_absent = allow_absent

    def __repr__(self):
        """Codelike representation for debugging."""
        return '{}({!r}, {!r}, {!r}, allow_absent={!r})'.format(
            type(self).__name__,
            self._target,
            self._name,
            self._value,
            self._allow_absent,
        )

    # FIXME: Make this work as a decorator, without changing how it works when
    # it is used as a context manager.

    def __enter__(self):
        """Patch the attribute."""
        try:
            self._old = getattr(self._target, self._name)
        except AttributeError:
            if not self._allow_absent:
                raise
            self._absent = True
        else:
            self._absent = False

        setattr(self._target, self._name, self._value)

    def __exit__(self, exc_type, exc_value, traceback):
        """Unpatch the attribute."""
        del exc_type, exc_value, traceback

        if self._absent:
            delattr(self._target, self._name)
        else:
            setattr(self._target, self._name, self._old)


__all__ = [thing.__name__ for thing in (
    Announce,
    Closing,
    Suppress,
    MonkeyPatch,
    MonkeyPatchAlt,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
