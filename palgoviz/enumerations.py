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

"""Some enumerations."""

__all__ = [
    'OrderedEnum',
    'CodeReprEnum',
    'BearBowl',
    'BitsetEnum',
    'Guests',
]

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

    def isdisjoint(self, other):
        """Check if disjoint with other."""
        if not isinstance(other, type(self)):
            raise TypeError('isdisjoint() not supported with types'
                            f'other than {type(self).__name__}')
        return not (self & other)

    def overlaps(self, other):
        """Check if overlaps with other."""
        if not isinstance(other, type(self)):
            raise TypeError('overlaps() not supported with types'
                            f'other than {type(self).__name__}')
        return bool(self & other)


class Guests(BitsetEnum):
    """Potential party and/or trial guests."""

    # Aligning up enumeration constants, common in many languages, is less
    # common in Python. flake8 says: E221 multiple spaces before operator
    # (This message is a bit confusing since "=" is not an operator in Python.)
    # In this specific case, we suppress the message and use this style.

    ALICE   = A = enum.auto()  # noqa: E221
    BOB     = B = enum.auto()  # noqa: E221
    CASSIDY = C = enum.auto()  # noqa: E221
    DEREK   = D = enum.auto()  # noqa: E221
    ERIN    = E = enum.auto()  # noqa: E221
    FRANK   = F = enum.auto()  # noqa: E221
    GERALD  = G = enum.auto()  # noqa: E221
    HEATHER = H = enum.auto()  # noqa: E221

    PARTY   = ALICE | CASSIDY | FRANK     # noqa: E221
    PARTY2  = ALICE | BOB | ERIN | FRANK  # noqa: E221

    # Trials can have guests and are not parties.
    # Trials are needed because the parties were a tad too wild.

    ALICE_TRIAL   = BOB | CASSIDY             # noqa: E221
    BOB_TRIAL     = ALICE | HEATHER           # noqa: E221
    CASSIDY_TRIAL = 0
    ERIN_TRIAL    = CASSIDY | DEREK | GERALD  # noqa: E221
    FRANK_TRIAL   = BOB | CASSIDY | DEREK     # noqa: E221


if __name__ == '__main__':
    import doctest
    doctest.testmod()
