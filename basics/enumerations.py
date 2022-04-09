#!/usr/bin/env python

"""Some enumerations."""

import enum
import functools


@functools.total_ordering
class OrderedEnum(enum.Enum):
    """
    Enumeration whose instances support order comparisons on their values.
    """
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value < other.value


class CodeReprEnum(enum.Enum):
    """Enumeration whose instances' repr is Python code."""
    def __repr__(self):
        return str(self)


@enum.unique
class BearBowl(OrderedEnum, CodeReprEnum):
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


class BitsetEnum(enum.Flag):
    """Instances of BitsetEnum support - and comparison operators."""

    def __sub__(self, other):
        """Set difference."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self & ~other

    def __le__(self, other):
        """Subset check."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self & other == self

    def __lt__(self, other):
        """Proper subset check."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self != other and self.__le__(other)

    def __ge__(self, other):
        """Superset check."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self & other == other

    def __gt__(self, other):
        """Proper superset check."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self != other and self.__ge__(other)

    def __len__(self):
        """Number of items in bitset."""
        return self.value.bit_count()

    # FIXME: This kind of method should never return NotImplemented. Unlike
    # "magic" methods like __le__, which are called indirectly (for operators
    # like "<"), isdisjoint is meant to be called directly. So if it checks a
    # type and finds it to be wrong, it should directly raise TypeError.
    def isdisjoint(self, other):
        """Check if disjoint with other."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return not (self & other)


class Guests(BitsetEnum):
    """Potential party and/or trial guests."""

    ALICE   = A = enum.auto()
    BOB     = B = enum.auto()
    CASSIDY = C = enum.auto()
    DEREK   = D = enum.auto()
    ERIN    = E = enum.auto()
    FRANK   = F = enum.auto()
    GERALD  = G = enum.auto()
    HEATHER = H = enum.auto()

    PARTY   = ALICE | CASSIDY | FRANK
    PARTY2  = ALICE | BOB | ERIN | FRANK

    # Trials can have guests and are not parties
    # Trials are needed because the parties were a tad too wild.

    ALICE_TRIAL   = BOB | CASSIDY
    BOB_TRIAL     = ALICE | HEATHER
    CASSIDY_TRIAL = 0
    ERIN_TRIAL    = CASSIDY | DEREK | GERALD
    FRANK_TRIAL   = BOB | CASSIDY | DEREK


if __name__ == '__main__':
    import doctest
    doctest.testmod()
