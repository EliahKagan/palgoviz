"""Context managers."""

import sys


class Announce:
    """Context manager to announce starting and finishing a task, by name."""

    __slots__ = ('_name', '_out', '_canceled')

    def __init__(self, name, *, out=None):
        """Create an announcer for a task of a specified name."""
        self._name = name
        self._out = (sys.stdout if out is None else out)
        self._canceled = False

    def __repr__(self):
        """Informative, but not runnable, representation of this object."""
        parts = []
        parts.append(f'name={self.name!r}')
        if self.out is not None:
            parts.append(f'out={self.out!r}')
        parts.append(f'canceled={self.canceled!r}')

        return f'<{type(self).__name__}: {", ".join(parts)}>'

    def __enter__(self):
        """Announce the task is starting, unless cancel() has been called."""
        self._put(f'Starting task {self._name}.')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Announce the task has finished, unless cancel() has been called."""
        del exc_value, traceback

        if self.canceled:
            return

        if exc_type is None:
            self._put(f'Finished task {self.name}.')
        else:
            self._put(f'{exc_type.__name__} raised in task {self.name}.')

    @property
    def name(self):
        """The name of the task."""
        return self._name

    @property
    def out(self):
        """The output file object that messages are written to."""
        return self._out

    @property
    def canceled(self):
        """Whether or not cancel() has been called to cancel printing."""
        return self._canceled

    def cancel(self):
        """Cancel printing any further messages."""
        self._canceled = True

    def _put(self, message):
        """Output a message, if cancel() hasn't been called."""
        if not self.canceled:
            print(message, file=self._out)


class Closing:
    """Context manager to call close. Like contextlib.closing."""

    __slots__ = ('_closeable_object',)

    def __init__(self, closeable_object):
        """Create a context manager that will close a particular object."""
        self._closeable_object = closeable_object

    def __repr__(self):
        """Representation of this object as Python code."""
        return f'{type(self).__name__}({self._closeable_object!r})'

    def __enter__(self):
        """Return the closeable object."""
        return self._closeable_object

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the closeable object."""
        del exc_type, exc_value, traceback
        self._closeable_object.close()


class Suppress:
    """Context manager to swallow some exceptions. Like contextlib.suppress."""

    __slots__ = ('_exception_types',)

    def __init__(self, *exception_types):
        """Create a context manager that "suppresses" given exception types."""
        self._exception_types = exception_types

    def __repr__(self):
        """Representation of this object, possibly runnable as Python code."""
        arguments = ", ".join(t.__name__ for t in self._exception_types)
        return f'{type(self).__name__}({arguments})'

    def __enter__(self):
        """Do nothing on entry to the context manager. (See __exit__.)"""

    def __exit__(self, exc_type, exc_value, traceback):
        """If an exception of an appropriate type was raised, suppress it."""
        del exc_value, traceback
        return issubclass(exc_type, self._exception_types)


class MonkeyPatch:
    """Context manager to patch and unpatch an attribute."""

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

    def __repr__(self):
        """Representation of this object as Python code."""
        return (f'{type(self).__name__}({self._target!r}, {self._name!r}, '
                f'{self._new_value!r}, allow_absent={self._allow_absent!r})')

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
