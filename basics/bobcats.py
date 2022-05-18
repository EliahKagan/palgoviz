"""
The scourge of immutable bobcats.

This code modeled regular and extra-fierce bobcats, until most of it was lost
in a bobcat attack. Fortunately, unit tests in test_bobcats.py were not harmed.
"""

from numbers import Number, Complex, Real

class Bobcat:
    """
    A named bobcat.

    Direct instances of this class represent bobcats distinguishable solely by
    name. Subclasses are not required to preserve this invariant.
    """

    __slots__ = ('_name',)

    def __init__(self, name):
        """Create a Bobcat with a specified name."""
        if not isinstance(name, str):
            raise TypeError('Names must be strings.')

        if not name:
            raise ValueError('Names must be non-empty.')

        self._name = name

    def __repr__(self):
        """Represent this Bobcat as Python code."""
        return f'{type(self).__name__}({self.name!r})'

    def __str__(self):
        """How this bobcat is announced at campaign fundraisers."""
        return self.name + ' the bobcat'

    def __eq__(self, other):
        """Check if two Bobcats have the same name."""
        if not isinstance(other, Bobcat):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self):
        """The name bobcat naming robots gave to this bobcat."""
        return self._name


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

    __slots__ = ('_fierceness', )

    FIERCENESS_CUTOFF = 9000

    def __init__(self, name, fierceness):
        """Create a FierceBobcat with a specified name and fierceness."""
        if not isinstance(name, str):
            raise TypeError('Names must be strings.')

        if not name:
            raise ValueError('Names must be non-empty.')

        if not isinstance(fierceness, Number):
            raise TypeError('Fierceness must be a number.')

        if not isinstance(fierceness, Real):
            raise TypeError('Fierceness must be real.')

        if not fierceness > self.FIERCENESS_CUTOFF:
            raise ValueError(f'Fiercess must be over {self.FIERCENESS_CUTOFF}')

        self._name = name
        self._fierceness = fierceness

    def __repr__(self):
        """Represent this FierceBobcat as Python code with parameter names."""
        return f'{type(self).__name__}(name={self.name!r}, fierceness={self.fierceness!r})'

    # No need to override __str__ method

    def __eq__(self, other):
        # FIXME: may not need this
        if type(other) is Bobcat:
            return False

        if not isinstance(other, FierceBobcat):
            return NotImplemented

        return self.name == other.name and self.fierceness == other.fierceness

    def __hash__(self):
        return hash((self.name, self.fierceness))

    @property
    def name(self):
        """The name bobcat naming robots gave to this bobcat."""
        return self._name

    @property
    def fierceness(self):
        """The fierceness of this fierce bobcat."""
        return self._fierceness
