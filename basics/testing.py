"""Test helpers used by multiple test modules."""


class ShortReprMeta(type):
    """Metaclass to use class names as reprs, to improve doctest clarity."""

    def __repr__(self):
        """Represent a class as its bare name."""
        return self.__name__


__all__ = [ShortReprMeta.__name__]
