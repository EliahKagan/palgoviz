"""Mutable collections using hashing or similar techniques."""

from collections.abc import MutableMapping
import itertools
import math


# FIXME: Simplify this further, making it an orthodox direct address table
# where start=0 always.
class IntKeyTable(MutableMapping):
    """A direct address table, the simplest kind of mutable mapping."""

    __slots__ = ('_values', '_start', '_len')

    _absent = object()  # Sentinel representing the absence of an entry.

    def __init__(self, start, stop, other=()):
        """Create an IntKeyTable allowing keys in range(start, stop)."""
        if not (isinstance(start, int) and isinstance(stop, int)):
            raise TypeError('start and stop must (both) be of type int')
        if stop < start:
            raise ValueError('stop must not precede start')
        self._values = [self._absent] * (stop - start)
        self._start = start
        self._len = 0
        self.update(other)

    def __repr__(self):
        """Python code representation of this IntKeyTable."""
        typename = type(self).__name__
        item_strings = (f'{key!r}: {value!r}' for key, value in self.items())
        dict_repr = '{%s}' % ", ".join(item_strings)
        return f'{typename}({self.start!r}, {self.stop!r}, {dict_repr})'

    def __len__(self):
        """The number of key-value pairs currently stored in this table."""
        return self._len

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        value = self._values[self._index(key)]
        if value is self._absent:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        index = self._index(key)
        if self._values[index] is self._absent:
            self._len += 1
        self._values[index] = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key maps to no value."""
        index = self._index(key)
        if self._values[index] is self._absent:
            raise KeyError(key)
        self._values[index] = self._absent
        self._len -= 1

    def __iter__(self):
        """Iterate through the keys of this IntKeyTable."""
        return (key for (key, value) in enumerate(self._values, self.start)
                if value is not self._absent)

    @property
    def start(self):
        """The minimum allowed key in this IntKeyTable object."""
        return self._start

    @property
    def stop(self):
        """One greater than the maximum in this IntKeyTable object."""
        return self.start + self.capacity

    @property
    def capacity(self):
        """The number of possible keys."""
        return len(self._values)

    def _index(self, key):
        """Get the index where a given key is or would be stored."""
        if not isinstance(key, int):
            raise TypeError(f'key must be int, not {type(key).__name__}')
        if not self.start <= key < self.stop:
            raise ValueError(f'key {key!r} out of range')
        return key - self.start


class _HashTableEntry:
    """A key-value pair. This is an implementation detail of HashTable."""

    __slots__ = ('key', 'value')

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.key!r}, {self.value!r})'

    def matches(self, key):
        """Tell if this entry's key matches the given key."""
        return self.key is key or self.key == key


class HashTable(MutableMapping):
    """Hash-based mutable mapping. Like dict but with no order guarantees."""

    __slots__ = ('_buckets', '_len')

    _MIN_BUCKETS = 8
    _SHRINK_THRESHOLD = 0.25
    _GROW_THRESHOLD = 0.75
    _REHASH_LOAD_FACTOR = 0.5

    assert _SHRINK_THRESHOLD < _REHASH_LOAD_FACTOR < _GROW_THRESHOLD

    @classmethod
    def fromkeys(cls, iterable, value=None):
        """Make a HashTable from an iterable of keys, mapping all to value."""
        return cls((key, value) for key in iterable)

    def __init__(self, other=()):
        """Make a HashTable, optionally from a mapping or iterable of items."""
        self.clear()
        self.update(other)

    def __repr__(self):
        """Python code representation of this HashTable."""
        item_strings = (f'{key!r}: {value!r}' for key, value in self.items())
        dict_repr = '{%s}' % ", ".join(item_strings)
        return f'{type(self).__name__}({dict_repr})'

    def __len__(self):
        """The number of key-value pairs currently stored in this HashTable."""
        return self._len

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        bucket = self._get_bucket(key)
        try:
            return next(entry.value for entry in bucket if entry.matches(key))
        except StopIteration:
            raise KeyError(key) from None

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        bucket = self._get_bucket(key)
        try:
            existing = next(entry for entry in bucket if entry.matches(key))
        except StopIteration:
            bucket.append(_HashTableEntry(key, value))
            self._len += 1
            self._maybe_grow()
        else:
            existing.value = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key maps to no value."""
        bucket = self._get_bucket(key)
        try:
            index = next(index for index, entry in enumerate(bucket)
                         if entry.matches(key))
        except StopIteration:
            raise KeyError(key) from None
        else:
            bucket[index] = bucket[-1]
            del bucket[-1]
            self._len -= 1
            self._maybe_shrink()

    def __iter__(self):
        """Iterate through the keys of this HashTable."""
        return (entry.key for entry in self._entries)

    def clear(self):
        """Remove all items from this HashTable."""
        self._buckets = [[] for _ in range(self._MIN_BUCKETS)]
        self._len = 0

    @property
    def _load_factor(self):
        return len(self) / len(self._buckets)

    @property
    def _target_bucket_count(self):
        return len(self) / self._REHASH_LOAD_FACTOR

    @property
    def _entries(self):
        return itertools.chain.from_iterable(self._buckets)

    def _get_bucket(self, key):
        return self._buckets[hash(key) % len(self._buckets)]

    def _rehash(self, new_bucket_count):
        new_buckets = [[] for _ in range(new_bucket_count)]
        for entry in self._entries:
            new_buckets[hash(entry.key) % new_bucket_count].append(entry)
        self._buckets = new_buckets

    def _maybe_grow(self):
        if self._load_factor > self._GROW_THRESHOLD:
            self._rehash(math.ceil(self._target_bucket_count))

    def _maybe_shrink(self):
        if self._load_factor < self._SHRINK_THRESHOLD:
            new_bucket_count = max(self._MIN_BUCKETS,
                                   math.floor(self._target_bucket_count))
            if new_bucket_count < len(self._buckets):
                self._rehash(new_bucket_count)
