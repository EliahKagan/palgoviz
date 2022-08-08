#!/usr/bin/env python

"""Some enumerations."""

import enum
import functools

import graphviz


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


class UmpireNetwork:
    """
    Graph for contact tracing enumerators in a BitsetEnum.

    It's bad enough that the parties went too far, and the criminal justice
    system got involved, but it turns out the Guests are also the center of an
    epidemic of umpirism. Parties and trials both afford the opportunity for
    any umpire in attendance to inadvertently cause anyone else to also become
    an umpire. At this point, it's unknown who was an umpire when or for how
    long, so we're just drawing an undirected graph with edges between each
    guest and each event that guest attended. By inspecting the graph, one can
    see all guests who attended any party and all parties any guest attended.
    Guests a distance 2 apart in the graph attended at least one common event.

    Guests and events are vertices in the graph. Guests' shapes and colors
    differ from events' shapes and colors, to avoid confusion. No knowledge of
    what guests or events exist is hard coded in this class, which should work
    just as well for other BitsetEnums. But an UmpireNetwork instance supports
    only one enum, determined as of the first call to the event method. Vertex
    labels are parsed from enumerator names by splitting underscore-separated
    words and having just the initial letter of each word capitalized. Guest
    labels can't be customized. Custom labels can be given for events when
    adding the event. Events without multiple attendees are completely ignored,
    except that if the first call attempts to add such an event, the enum for
    the UmpireNetwork instance is still set.
    """

    __slots__ = ('_vertices', '_edges')

    def __init__(self):
        """Create a new umpire contact-tracing network."""
        self._vertices = set()
        self._edges = set()

    def event(self, guests, label=None):
        """Add an event, passing a bitfield of its guests."""
        if guests.value.bit_count < 2 or guests in self._vertices:
            return
        self._vertices


__all__ = [thing.__name__ for thing in (
    OrderedEnum,
    CodeReprEnum,
    BearBowl,
    BitsetEnum,
    Guests,
    UmpireNetwork,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
