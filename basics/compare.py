"""
Types that compare in special ways.

The main use for this module (at least currently) is to help in building tests
for code that sorts or searches, or otherwise makes use of order comparisons.
"""

import enum


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
    # FIXME: Implement this.
