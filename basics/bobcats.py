"""The scourge of immutable bobcats."""


class Bobcat:
    """
    A named bobcat.

    Direct instances of this class represent bobcats distinguishable solely by
    name. Subclasses are not required to preserve this property.
    """


class FierceBobcat:
    """
    A bobcat so fierce its name might not be unique.

    Naming robots run away so fast from bobcats whose fierceness exceeds 9000
    that they don't always take the time to make sure the name they give is not
    the name of any other bobcat. Fortunately, no two bobcats are equally
    fierce. Instances of this class represent such fierce bobcats.
    """
