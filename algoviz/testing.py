"""
Test helpers used by code in the algoviz package and/or notebooks.

If a test helper is not (meant to be) used outside the modules in tests/, but
it is used by multiple test modules or otherwise shouldn't be inside a "test_*"
module, then it should be in a non-public module in tests/, rather than here.
"""

import gc
import platform

if platform.python_implementation() == 'CPython':
    def collect_if_not_ref_counting():
        """Force a collection if we might not be using reference counting."""
        # CPython always refcounts as its primary GC strategy, so do nothing.
else:
    def collect_if_not_ref_counting():
        """Force a collection if we might not be using reference counting."""
        gc.collect()


class ShortReprMeta(type):
    """Metaclass to use class names as reprs, to improve doctest clarity."""

    def __repr__(self):
        """Represent a class as its bare name."""
        return self.__name__


__all__ = [thing.__name__ for thing in (
    collect_if_not_ref_counting,
    ShortReprMeta,
)]
