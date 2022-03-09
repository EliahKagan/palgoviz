"""The scourge of immutable bobcats."""


class Bobcat:
    """
    A named bobcat.

    Direct instances of this class represent bobcats distinguishable solely by
    name. Subclasses are not required to preserve this property.
    """

    __slots__ = ('_name',)

    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError('got non-string value for bobcat name')
        if not name:
            raise ValueError('bobcat names must be least one character long')
        self._name = name

    def __repr__(self):
        """Representation of this bobcat that can be run as Python code."""
        return f'{type(self).__name__}({self.name!r})'

    def __str__(self):
        """How this bobcat is announced at campaign fundraisers."""
        return f'{self.name} the bobcat'

    def __eq__(self, other):
        """Check if this and another object represent the same bobcat."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self):
        """The name bobcat-naming robots gave to this bobcat."""
        return self._name
