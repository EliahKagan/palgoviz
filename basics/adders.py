"""Callables that add a fixed value to their argument."""

__all__ = ['make_adder', 'Adder', 'AdderA']

import attrs


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


@attrs.frozen
class AdderA:
    """
    Callable object that adds its argument to the addend given on construction.

    This alternative implementation of Adder is much shorter, due to its use of
    the attrs library. (It is made with the modern attrs API.)

    >>> a = AdderA(7)
    >>> a(4)
    11
    >>> a(10)
    17
    >>> AdderA(6)(2)
    8
    >>> AdderA('cat')
    AdderA(left_addend='cat')
    >>> _(' dog')
    'cat dog'
    >>> s = {AdderA(7), AdderA(7), AdderA(6), AdderA(7.0)}
    >>> s == {AdderA(6), AdderA(7)}
    True
    >>> a.left_addend
    7
    >>> a.left_addend = 8  # Fairly clear, and inherits from AttributeError.
    Traceback (most recent call last):
      ...
    attr.exceptions.FrozenInstanceError
    >>> a.right_addend = 5  # Unfortunately doesn't make clear what the bug is.
    Traceback (most recent call last):
      ...
    attr.exceptions.FrozenInstanceError
    """

    left_addend = attrs.field()
    """This adder's left addend."""

    def __call__(self, right_addend):
        """Add this adder's left addend to the argument."""
        return self.left_addend + right_addend


if __name__ == '__main__':
    import doctest
    doctest.testmod()
