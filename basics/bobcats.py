"""The scourge of immutable bobcats."""

from numbers import Real


class Bobcat:
    """
    A named bobcat.

    Direct instances of this class represent bobcats distinguishable solely by
    name. Subclasses are not required to preserve this invariant.
    """

    __slots__ = ('__name',)

    def __init__(self, name):
        """Make a bobcat with the specified name."""
        if not isinstance(name, str):
            raise TypeError('got non-string value for bobcat name')
        if not name:
            raise ValueError('bobcat names must be least one character long')
        self.__name = name

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
        return self.__name


class FierceBobcat(Bobcat):
    """
    A bobcat so fierce its name might not be unique.

    Naming robots run away so fast from bobcats whose fierceness exceeds 9000
    that they don't always take the time to make sure the name they give is not
    the name of any other bobcat. Fortunately, no two bobcats with the same
    name are equally fierce. (No one knows why, but bobcat scholars -- those of
    them who are still with us, I mean -- suspect equal fierceness only happens
    in the same family, where everyone has a different name.)

    Instances of this class represent such fierce bobcats.
    """

    __slots__ = ('_fierceness',)

    FIERCENESS_CUTOFF = 9000
    """Fierceness must be strictly greater than this level."""

    def __init__(self, name, fierceness):
        """Make a bobcat with the specified name and fierceness."""
        super().__init__(name)

        if not isinstance(fierceness, Real):
            raise TypeError('fierceness must be a real number')

        if fierceness <= self.FIERCENESS_CUTOFF:
            raise ValueError(
                f'a fierceness of {fierceness} is not fierce for a bobcat')

        self._fierceness = fierceness

    def __repr__(self):
        """Representation of this bobcat that can be run as Python code."""
        return (type(self).__name__
                + f'(name={self.name!r}, fierceness={self.fierceness!r})')

    def __eq__(self, other):
        """Check if this and other represent the same fierce bobcat."""
        if not isinstance(other, type(self)):
            # Ensure we're unequal to bobcats that don't know about fierceness.
            return False if isinstance(other, Bobcat) else NotImplemented

        return super().__eq__(other) and self.fierceness == other.fierceness

    def __hash__(self):
        return hash((self.name, self.fierceness))

    @property
    def fierceness(self):
        return self._fierceness
