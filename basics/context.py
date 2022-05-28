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
