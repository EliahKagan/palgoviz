"""
Shared test helpers.

These are test helpers that multiple test modules use, or that otherwise should
not appear in any particular test module, but that are implementation details
of the test suite itself. That is to say that they are not used in the palgoviz
package, not even in doctests there (though they may be used in doctests in any
files in tests/, of course), and they are not intended for use in notebooks.

Shared test helpers that are not considered private implementation details of
the test suite appear in palgoviz.testing instead of this nonpublic module.
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


class NonSelfEqual:
    """
    Pathological objects that are not even equal to themselves.

    Objects can, in nearly all cases, be assumed equal to themselves. When a
    non-self-equal object, such as any instance of this class, does exist, it
    is usually the responsibility of the code that introduces such an object to
    ensure it is never used in any ways that would cause problems. But there
    are a few situations where one ought to make specific guarantees about the
    handling of such objects, because floating point NaNs have this property.

    The purpose of this class is to facilitate tests of behaviors that hold for
    NaN values, including but not limited to math.nan, mainly to ensure NaNs
    aren't special-cased by accident. (Other than NaNs and for testing, there
    are likely no good justifications for introducing a non-self-equal object.)
    """

    __slots__ = ()

    def __repr__(self):
        """Python code representation for debugging."""
        return f'{type(self).__name__}()'

    def __eq__(self, _):
        """A NonSelfEqual instance is never equal to anything, even itself."""
        return False

    def __hash__(self):
        """
        Provide consistent but deliberately poor quality hashing.

        For performance, we should just use __hash__ = object.__hash__, or
        otherwise hash based on the id. But it is more important to test that
        separate instances will not wrongly match, so force a hash collision
        every time by every instance having the same arbitrary hash code.
        """
        return -9977361389391351282


__all__ = [thing.__name__ for thing in (
    CommonIteratorTests,
    NonSelfEqual,
)]
