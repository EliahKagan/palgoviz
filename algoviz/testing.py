"""Test helpers used by multiple modules."""

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


__all__ = [thing.__name__ for thing in (
    collect_if_not_ref_counting,
)]
