#!/usr/bin/env python

"""Callables that add a fixed value to their argument."""


def make_adder(left_addend):
    """
    Create a function that adds its argument to the already-given addend.

    >>> f = make_adder(7)
    >>> f(4)
    11
    >>> f(10)
    17
    >>> make_adder(6)(2)
    8
    >>> s = make_adder('cat')
    >>> s(' dog')
    'cat dog'
    """
    def adder(right_addend):
        return left_addend + right_addend
    return adder


class Adder:
    """
    Callable object that adds its argument to the addend given on construction.

    The fixed addend an Adder stores and uses is a left addend, which matters
    in some noncommutative meanings of "+", such as sequence concatenation.
    This is the class version of make_adder, with some more features classes
    allow.

    >>> a = Adder(7)
    >>> a(4)
    11
    >>> a(10)
    17
    >>> Adder(6)(2)
    8
    >>> Adder('cat')
    Adder('cat')
    >>> _(' dog')
    'cat dog'
    >>> {Adder(7), Adder(7), Adder(6), Adder(7.0)} == {Adder(6), Adder(7)}
    True
    >>> a.left_addend
    7
    >>> a.left_addend = 8
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute 'left_addend'
    >>> a.right_addend = 5  # This would be a conceptual mistake.
    Traceback (most recent call last):
      ...
    AttributeError: 'Adder' object has no attribute 'right_addend'
    """

    __slots__ = ('_left_addend',)

    def __init__(self, left_addend):
        """Construct an adder with left_addend."""
        self._left_addend = left_addend

    def __repr__(self):
        """Representation of this adder as Python code."""
        return f"{type(self).__name__}({self.left_addend!r})"

    def __call__(self, right_addend):
        """Add this adder's left addend to the argument."""
        return self.left_addend + right_addend

    def __eq__(self, other):
        """Check if two adders have the same left_addend."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.left_addend == other.left_addend

    def __hash__(self):
        return hash(self.left_addend)

    @property
    def left_addend(self):
        """This adder's left addend."""
        return self._left_addend


if __name__ == '__main__':
    import doctest
    doctest.testmod()
