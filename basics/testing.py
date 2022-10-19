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


__all__ = [thing.__name__ for thing in (
    collect_if_not_ref_counting,
    NonSelfEqual,
)]
