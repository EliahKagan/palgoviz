"""Some simple code, for unit testing."""

from abc import ABC, abstractmethod
import enum
import sys
import itertools


MY_NONE = None


class Widget:
    """Something with size and color attributes, disallowing new attributes."""

    __slots__ = ('size', 'color')

    def __init__(self, size, color):
        """Create a new widget of the specified size and color."""
        self.size = size
        self.color = color


def answer():
    """
    Return the int said to answer the question of life/the universe/everything.
    """
    return 42


def is_sorted(items):
    """Check if an iterable is sorted."""
    my_items = list(items)
    return my_items == sorted(my_items)


def alert(message):
    """Print an alert to standard error, with a simple "alert:" prefix."""
    print(f'alert: {message}', file=sys.stderr)


def bail_if(condition):
    """Exit indicating failure if the condition evaluates as true."""
    if condition: sys.exit(1)


class Squarer(ABC):
    """Abstract class representing squarers."""

    __slots__ = ()

    @abstractmethod
    def __call__(self, number):
        """Square a number."""
        ...

    def __repr__(self):
        """Represent this Squarer as Python code."""
        return f"{type(self).__name__}()"

    def __eq__(self, other):
        """Check if two Squarers are of the same type."""
        if not isinstance(other, Squarer):
            return NotImplemented
        return type(self) is type(other)

    def __hash__(self):
        return hash(type(self))


class MulSquarer(Squarer):
    """Callable object that squares numbers with the * operator."""

    __slots__ = ()

    def __call__(self, number):
        """
        Square a number using the * operator.

        >>> m = MulSquarer()
        >>> m(3)
        9
        """
        return number * number


class PowSquarer(Squarer):
    """Callable object that squares numbers with the ** operator."""

    __slots__ = ()

    def __call__(self, number):
        """
        Square a number using the ** operator.

        >>> p = PowSquarer()
        >>> p(3)
        9
        """
        return number**2


def make_squarer():
    """
    Return a function that squares.

    >>> f = make_squarer()
    >>> f(3)
    9
    """
    return lambda x: x**2


def _check_toggle_param(start):
    if not isinstance(start, bool):
        raise TypeError(f'{start} is not an instance of bool.')


class Toggle:
    """
    Callable object returning alternating bools.

    >>> tf = Toggle(True)
    >>> tf()
    True
    >>> tf()
    False
    >>> tf()
    True
    >>> ft = Toggle(False)
    >>> ft()
    False
    >>> ft()
    True
    >>> ft()
    False
    """

    __slots__ = ('_state',)

    def __init__(self, start):
        """Create a Toggle from the start bool."""
        _check_toggle_param(start)
        self._state = start

    def __call__(self):
        """Flip the state."""
        old_state = self._state
        self._state = not self._state
        return old_state

    def __repr__(self):
        """Represent this Toggle as Python code."""
        return f"{type(self).__name__}({self._state})"

    def __eq__(self, other):
        """Check if two Togglers have the same state."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._state == other._state


def make_toggle(start):
    """
    Create a function that returns alternating bools.

    >>> tf = make_toggle(True)
    >>> tf()
    True
    >>> tf()
    False
    >>> tf()
    True
    >>> ft = make_toggle(False)
    >>> ft()
    False
    >>> ft()
    True
    >>> ft()
    False
    """
    _check_toggle_param(start)

    state = start

    def toggle():
        nonlocal state
        old_state = state
        state = not state
        return old_state

    return toggle


def make_toggle_alt(start):
    """
    Create a function that returns alternating bools, using itertools.cycle.

    >>> tf = make_toggle_alt(True)
    >>> tf()
    True
    >>> tf()
    False
    >>> tf()
    True
    >>> ft = make_toggle_alt(False)
    >>> ft()
    False
    >>> ft()
    True
    >>> ft()
    False
    """
    _check_toggle_param(start)
    it = itertools.cycle([start, not start])
    return lambda: next(it)


# TODO: Remove all comparisons but __lt__ and use @functools.total_ordering.
@enum.unique
class BearBowl(enum.Enum):
    """
    A bowl of porridge Goldilocks tasted while trespassing in a bear kitchen.

    BearBowls compare by heat: a cooler bowl is less than a warmer bowl.

    Temperatures are in Kelvin.

    >>> BearBowl.TOO_COLD < BearBowl.JUST_RIGHT < BearBowl.TOO_HOT
    True
    """

    TOO_HOT = 5778
    """Approximate temperature of the sun."""

    JUST_RIGHT = 288
    """Non-fatal temperature for a bowl of porridge."""

    TOO_COLD = 95
    """Approximate surface temperature of Titan."""

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value >= other.value

    def __repr__(self):
        return str(self)
