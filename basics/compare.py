"""
Types that compare in special ways.

The main use for this module is to help in building tests for code that sorts,
searches, or otherwise operates based on order comparisons, though it may have
other uses.
"""


class OrderIndistinct:
    """
    Objects indistinguishable by the "<" and ">" operators.

    OrderIndistinct instances compare for equality by their value attribute,
    but when that attribute differs, both "<" and ">" still return False.

    The purpose of this class is to help in testing sorts for stability.
    """

    __slots__ = ('value',)

    def __init__(self, value):
        """Create a new OrderIndistinct object with a given value payload."""
        self.value = value

    def __repr__(self):
        """eval-able string representation."""
        return f'{type(self).__name__}({self.value!r})'

    def __eq__(self, other):
        """OrderIndistinct equality delegates to the value attributes."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        """No OrderIndistinct object is less than any other."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return False

    def __gt__(self, other):
        """No OrderIndistinct object is greater than any other."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return False

    def __le__(self, other):
        """Only equal OrderIndistinct objects are less than or equal."""
        return self.__eq__(other)

    def __ge__(self, other):
        """Only equal OrderIndistinct objects are greater than or equal."""
        return self.__eq__(other)
