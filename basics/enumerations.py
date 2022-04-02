#!/usr/bin/env python

"""Some enumerations."""

import enum
import functools


@functools.total_ordering
@enum.unique
class BearBowl(enum.Enum):
    """
    A bowl of porridge Goldilocks tasted while trespassing in a bear kitchen.

    BearBowls compare by heat: a cooler bowl is less than a warmer bowl.

    Temperatures are in Kelvin.

    >>> BearBowl.TOO_COLD < BearBowl.JUST_RIGHT < BearBowl.TOO_HOT
    True
    """

    TOO_COLD = 95
    """Approximate surface temperature of Titan."""

    JUST_RIGHT = 288
    """Non-fatal temperature for a bowl of porridge."""

    TOO_HOT = 5778
    """Approximate temperature of the sun."""

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
