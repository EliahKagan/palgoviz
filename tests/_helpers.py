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


class Cell:
    """
    A box holding an object, allowing reassignment.

    This is used directly to implement test_sequences.FixedSizeBuffer, and also
    as a base class for WRCell below, which adds support for weak references.
    """

    __slots__ = ('value',)

    def __init__(self, value):
        """Create a cell with the given starting value."""
        self.value = value

    def __repr__(self):
        """Code-like representation, for debugging."""
        return f'{type(self).__name__}({self.value!r})'


class WRCell(Cell):
    """
    A Cell that supports being referred to by weak references.

    This is used to test that all (strong) references from a container under
    test to a just-removed element have been relinquished.

    (A container shouldn't usually keep any weak references to former elements
    either. But doing so wouldn't prolong the elements' lifetimes, it is
    nontrivial to test for that, and it is very unlikely that this would be
    done by accident, since weak reference creation is never implicit. So it's
    neither necessary nor worthwhile to test for that.)

    A clearer name would be _WeakReferenceableCell, but that would cause list
    reprs to be excessively long and difficult to read when debugging or
    examining test output.
    """

    __slots__ = ('__weakref__',)


class CWRCell(WRCell):
    """A comparable WRCell. Order comparison delegates to boxed elements."""

    __slots__ = ()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.value == other.value
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, type(self)):
            return self.value != other.value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, type(self)):
            return self.value <= other.value
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, type(self)):
            return self.value >= other.value
        return NotImplemented


class WeakReferenceable:
    """
    An otherwise uninteresting object that weak references can refer to.

    A non-slotted class would also be weak-referenceable but would readily hold
    attributes. WeakReferenceable is for tests where creating an attribute on
    the instance would be a bug in the test.
    """

    __slots__ = ('__weakref__',)

    def __repr__(self):
        """Representation as Python code."""
        return f'{type(self).__name__}()'


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
    Cell,
    WRCell,
    CWRCell,
    WeakReferenceable,
    NonSelfEqual,
)]
