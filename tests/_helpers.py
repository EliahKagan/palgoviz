"""
Shared test helpers.

These are test helpers that multiple test modules use, or that otherwise should
not appear in any particular test module, but that are implementation details
of the test suite itself. That is to say that they are not used in the algoviz
package, not even in doctests there (though they may be used in doctests in any
files in tests/, of course), and they are not intended for use in notebooks.

Shared test helpers that are not considered private implementation details of
the test suite appear in algoviz.testing instead of this nonpublic module.
"""

from collections.abc import Iterator

import pytest


class CommonIteratorTests:
    """Mixin for shared tests of iterators."""

    __slots__ = ()

    def instantiate(self, implementation):
        """
        Get an instance to test for shared iterator behavior.

        Derived classes should override this method if calling the factory with
        no arguments is not supported or is not the best way to produce an
        instance to test for shared iterator behavior.
        """
        return implementation()

    def test_is_iterator(self, implementation):
        """The result is an iterator."""
        result = self.instantiate(implementation)
        assert isinstance(result, Iterator)

    def test_iter_gives_same_object(self, implementation):
        """Calling the iter builtin on the result returns the same object."""
        result = self.instantiate(implementation)
        assert iter(result) is result

    def test_new_attributes_cannot_be_created(self, implementation):
        """
        Trying to create a new attribute on the result raises AttributeError.

        It is not always important that iterators behave this way, but it's a
        good default. Generators, and natively implemented standard library
        iterators such as those in itertools, raise AttributeError if
        nonexistent attributes are assigned to, and it's a good idea for custom
        iterators to behave that way in the absence of a reason (or at least a
        preference) otherwise.
        """
        result = self.instantiate(implementation)
        with pytest.raises(AttributeError):
            result.blah = 42


__all__ = [thing.__name__ for thing in (
    CommonIteratorTests,
)]
