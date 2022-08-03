"""Mutable sequences."""

from collections.abc import MutableSequence


class Vec(MutableSequence):
    """
    A MutableSequence adapting a fixed-size Sequence that supports __setitem__.

    Vec is a list-like type. Each instance stores elements in a non-resizing
    buffer. Sometimes it allocates a new buffer of a different size and copies
    all element references from old to new (then the old buffer can be garbage
    collected). A Vec's "capacity" is the size of its current buffer; len on a
    Vec gives the number of current elements, which is at most the capacity but
    often smaller. Capacity is changed at times, and by amounts, chosen so any
    series of n append and/or pop operations takes O(n) time. That is, append
    and pop take amortized O(1) time, as they do on list objects.

    In this initial Vec implementation, operations keep capacity the same or
    increase it; capacity is never decreased. A Vec object's space complexity
    is thus linear in the maximum length it has ever reached. This class will
    later be augmented to shrink capacity. [TODO: Then, update this paragraph.]

    To construct a Vec, a get_buffer function (or other callable) is passed as
    a mandatory keyword-only argument. For example, lambda k, x: [x] * k could
    be used. But the returned sequence need not support any mutating operations
    except setting items; it may be fixed-length, and Vec shall always treat it
    as if it is. In addition, a single positional argument may optionally be
    passed: an iterable of values to populate the Vec. This works the same as
    constructing an empty Vec and then then extending it with the iterable.

    Vec does not support slicing. It immediately raises TypeError if slicing is
    attempted. (Most sequences should support slicing and do. Some, such as
    collections.deque, do not. Sequence and MutableSequence do not require it.)
    Buffers from get_buffer might not support slicing, though that is not why
    Vec doesn't. Buffers support negative indexing, as must Vec. As detailed in
    test_grow.py, Vec supports some operations not required by MutableSequence.

    This overrides all abstract methods from MutableSequence, but no concrete
    ones. That is, all the default implementations are sufficient. This applies
    to methods MutableSequence introduces and those it inherits from Sequence.
    """
    # FIXME: Needs implementation.
