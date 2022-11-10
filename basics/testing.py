"""
Testing support.

See compare.py for code used in tests but specific to order comparison.
"""

from collections.abc import Iterator
import gc
import platform

import pytest

if platform.python_implementation() == 'CPython':
    def collect_if_not_ref_counting():
        """Force a collection if we might not be using reference counting."""
        # CPython always refcounts as its primary GC strategy, so do nothing.
else:
    def collect_if_not_ref_counting():
        """Force a collection if we might not be using reference counting."""
        gc.collect()


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
    collect_if_not_ref_counting,
    CommonIteratorTests,
)]
