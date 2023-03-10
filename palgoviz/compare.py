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

"""
Types that compare in special ways.

An important use for this module, though not the only use, is in building tests
for code that sorts, searches, or otherwise makes use of order comparisons.
"""

__all__ = ['WeakDiamond', 'Patient', 'OrderIndistinct']

import enum


# TODO: Decide whether WeakDiamond should implement __le__ and __ge__ at all.
@enum.unique
class WeakDiamond(enum.Enum):
    """
    Cardinal directions, ordered by how north they are.

    More southerly directions compare less than more northerly directions.

    This is a simple example of a weak ordering that isn't a total ordering.
    The equivalence classes are {NORTH}, {EAST, WEST}, {SOUTH}.
    """

    NORTH = enum.auto()
    SOUTH = enum.auto()
    EAST = enum.auto()
    WEST = enum.auto()

    def __lt__(self, other):
        """Check if this is farther south than another direction."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._rank < other._rank

    def __gt__(self, other):
        """Check if this is farther north than another direction."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._rank > other._rank

    def __le__(self, other):
        """
        Check if this is farther south than, or the same as, another direction.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self < other or self is other

    def __ge__(self, other):
        """
        Check if this is farther north than, or the same as, another direction.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self > other or self is other

    @property
    def _rank(self):
        """Totally ordered key selector. Helper for order comparisons."""
        match self:
            case WeakDiamond.SOUTH:
                return 0
            case WeakDiamond.EAST | WeakDiamond.WEST:
                return 1
            case WeakDiamond.NORTH:
                return 2

        raise AssertionError('unexpected enumeration instance')


# TODO: Decide whether Patient should implement __le__ and __ge__ at all.
class Patient:
    """
    Medical patient under triage.

    This is an example item type for a max priority queue.
    """

    __slots__ = ('_mrn', 'initials', 'priority')

    _next_mrn = 0  # The next patient gets this medical record number.

    def __init__(self, initials, starting_priority):
        """
        Create a patient record for triage.

        Use initials, not name, for privacy. Change them on patient request.

        Pass a starting priority (severity), which may need to be updated. (In
        some data structures, the record would need to be removed/reinserted.)
        """
        self._mrn = Patient._next_mrn
        Patient._next_mrn += 1
        self.initials = initials
        self.priority = starting_priority

    def __repr__(self):  # TODO: Maybe __str__ should be implemented too.
        """Informative representation of this record, useful for debugging."""
        mrn = f'mrn={self.mrn}'
        initials = f'initials={self.initials!r}'  # Include the quote marks.
        priority = f'priority={self.priority}'
        return f'<{type(self).__name__} {mrn} {initials} {priority}>'

    def __eq__(self, other):
        """
        Check if two patient records have the same medical record number.

        This actually checks the mrn rather than doing a simple "is" comparison
        because, although that would work for Patient objects constructed in
        the usual way, it would break serialization. This type is intended to
        work with the facilities supplied in the copy module and pickle module.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.mrn == other.mrn

    def __lt__(self, other):
        """Check if another patient should get priority over this one."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.priority < other.priority

    def __gt__(self, other):
        """Check if this patient should get priority over another one."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.priority > other.priority

    def __le__(self, other):
        """Check if a patient is, or should get priority over, this patient."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self < other or self == other

    def __ge__(self, other):
        """Check if this patient is, or should get priority over, a patient."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self > other or self == other

    def __hash__(self):
        return hash(self.mrn)

    @property
    def mrn(self):
        """Medical record number. This never changes and is never reused."""
        return self._mrn


class OrderIndistinct:
    """
    Objects indistinguishable by the "<" and ">" operators.

    OrderIndistinct instances compare for equality by their value attribute,
    but when that attribute differs, both "<" and ">" still return False.

    The purpose of this class is to help in testing sorts for stability.
    """

    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, OrderIndistinct):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, OrderIndistinct):
            return NotImplemented
        return False

    def __le__(self, other):
        return self.__eq__(other)

    def __gt__(self, other):
        return self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other)

    def __repr__(self):
        """Represent this OrderIndistinct as Python code and show its value."""
        return f"{type(self).__name__}({self.value!r})"
