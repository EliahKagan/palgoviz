#!/usr/bin/env python

"""Mutable sequences."""

from collections.abc import MutableSequence
import itertools

import more_itertools


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

    >>> import bisect, random
    >>> prng = random.Random(10947136274401272677)
    >>> a = Vec(range(20), get_buffer=lambda k, x: [x] * k)
    >>> prng.shuffle(a)
    >>> list(a)
    [4, 16, 18, 9, 17, 11, 12, 14, 8, 15, 1, 19, 5, 7, 13, 3, 6, 10, 2, 0]
    >>> b = Vec(get_buffer=lambda k, x: [x] * k)
    >>> for x in a: bisect.insort_right(b, x)
    >>> b  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Vec([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        get_buffer=<function <lambda> at 0x...>)
    """

    __slots__ = ('_get_buffer', '_buffer', '_length', '_can_shrink')

    _INITIAL_CAPACITY = 1
    """The size the buffer is grown to from zero."""

    _GROWTH_FACTOR = 2
    """Multiplier by which capacity is increased."""

    _SHRINK_TRIGGER = _GROWTH_FACTOR * 2
    """Capacity may decrease when it is this many times the length in use."""

    _ABSENT = object()
    """Sentinel representing the absence of an item, so debugging is easier."""

    def __init__(self, iterable=(), *, get_buffer, can_shrink=False):
        """Create a Vec with a get_buffer function and optional elements."""
        self._get_buffer = get_buffer
        self._buffer = ()
        self._length = 0
        self._can_shrink = can_shrink
        self.extend(iterable)

    def __repr__(self):
        """Code-like representation of this Vec, for debugging."""
        elements_str = f'[{", ".join(map(repr, self))}]'

        if isinstance(self._get_buffer, type):
            get_buffer_str = ', get_buffer=' + self._get_buffer.__qualname__
        else:
            get_buffer_str = ', get_buffer=' + repr(self._get_buffer)

        if self._can_shrink:  # NOTE: Must change with the default behavior.
            can_shrink_str = f', can_shrink={self._can_shrink}'
        else:
            can_shrink_str = ''

        typename = type(self).__name__
        return f'{typename}({elements_str}{get_buffer_str}{can_shrink_str})'

    def __len__(self):
        """The number of elements currently stored."""
        return self._length

    def __getitem__(self, index):
        """Get an item at an index. Slicing is not supported."""
        return self._buffer[self._normalize_index(index)]

    def __setitem__(self, index, value):
        """Set an item at an index. Slicing is not supported."""
        self._buffer[self._normalize_index(index)] = value

    def __delitem__(self, index):
        """Delete an item at an index. Slicing is not supported."""
        self._do_delitem(self._normalize_index(index))

    def __eq__(self, other):
        """Check if two Vec objects have equal elements in the same order."""
        if not isinstance(other, type(self)):
            return NotImplemented

        return (len(self) == len(other)
                and all(lhs == rhs for lhs, rhs in zip(self, other)))

    def __add__(self, other):
        """Concatenate Vec objects, self then other, making a new Vec."""
        if not isinstance(other, type(self)):
            return NotImplemented

        return type(self)(itertools.chain(self, other),
                          get_buffer=self._get_buffer,
                          can_shrink=self._can_shrink)

    def __radd__(self, other):
        """Concatenate Vec objects, other than self, making a new Vec."""
        if not isinstance(other, type(self)):
            return NotImplemented

        return type(self)(itertools.chain(other, self),
                          get_buffer=self._get_buffer,
                          can_shrink=self._can_shrink)

    def __mul__(self, count):
        """Repeat a vec object a given number of times, making a new Vec."""
        if not isinstance(count, int):
            return NotImplemented

        return type(self)(more_itertools.ncycles(self, count),
                          get_buffer=self._get_buffer,
                          can_shrink=self._can_shrink)

    def __rmul__(self, count):
        """Repeat a vec object a given number of times, making a new Vec."""
        return self.__mul__(count)

    def insert(self, index, value):
        """Insert a new item at a given index."""
        self._do_insert(self._normalize_index(index, allow_len=True), value)

    def copy(self):
        """Make a shallow copy."""
        return type(self)(self,
                          get_buffer=self._get_buffer,
                          can_shrink=self._can_shrink)

    def _do_delitem(self, left):
        """Helper for __delitem__. left is the validated nonnegative index."""
        self._length -= 1
        for right in range(left, self._length):
            self._buffer[right] = self._buffer[right + 1]
        self._buffer[self._length] = self._ABSENT

        if self._can_shrink:
            self._maybe_shrink()

    def _do_insert(self, left, value):
        """Helper for insert. left is the validated nonnegative index."""
        if self._length == len(self._buffer):
            self._grow()

        for right in range(self._length, left, -1):
            self._buffer[right] = self._buffer[right - 1]
        self._buffer[left] = value
        self._length += 1

    def _normalize_index(self, index, *, allow_len=False):
        """Check that an index is valid and normalize it to be nonnegative."""
        if not isinstance(index, int):
            typename = type(index).__name__
            raise TypeError(f"index must be 'int', got {typename!r}")

        ret = self._length + index if index < 0 else index

        if 0 <= ret < self._length or (allow_len and ret == self._length):
            return ret

        raise IndexError(f'index {index!r} is out of range')

    def _grow(self):
        """Switch to a bigger buffer."""
        new_capacity = max(self._length * self._GROWTH_FACTOR,
                           self._INITIAL_CAPACITY)

        self._reallocate_buffer(new_capacity)

    def _maybe_shrink(self):
        """If it looks like switching to a smaller buffer would help, do so."""
        if (self._length * self._SHRINK_TRIGGER < len(self._buffer)
                and self._INITIAL_CAPACITY <= self._length):
            self._reallocate_buffer(self._length)

    def _reallocate_buffer(self, new_capacity):
        """Get and switch to a new buffer of the given capacity."""
        assert(self._length <= new_capacity)

        new_buffer = self._get_buffer(new_capacity, self._ABSENT)

        for index in range(self._length):
            new_buffer[index] = self._buffer[index]

        self._buffer = new_buffer


__all__ = [Vec.__name__]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
