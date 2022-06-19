"""Mutable collections using hashing or similar techniques."""

import bisect
from collections.abc import Mapping, MutableMapping
import itertools
import math
import operator


class _Entry:
    """A key-value pair."""

    __slots__ = ('key', 'value')

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.key!r}, {self.value!r})'


class _NiceReprMapping(Mapping):
    """
    Mixin class providing a pretty, eval-able repr to a mapping.

    This is only suitable for mappings that can be constructed from a dict
    passed as the sole argument.
    """

    __slots__ = ()

    def __repr__(self):
        """Python code representation of this mapping."""
        item_strings = (f'{key!r}: {value!r}' for key, value in self.items())
        dict_repr = '{%s}' % ", ".join(item_strings)
        return f'{type(self).__name__}({dict_repr})'


class SortedFlatTable(_NiceReprMapping, MutableMapping):
    """
    A mutable mapping storing entries, sorted by key, in a non-nested sequence.

    All keys must be comparable by "<" and ">". The "==", "!=", "<=", and ">="
    operators will not be used to compare keys. Keys that are neither less nor
    greater than one another are regarded to be the same key, and keys must at
    least have a weak ordering. For example, using (arbitrary) sets as keys
    doesn't work, since the partial ordering of subsets is not a weak ordering.
    No special support is provided for pathological objects like math.nan.

    Searching takes O(log n) average and worst-case time. Inserting and
    deleting take O(n) average and worst-case time. Iterating through all items
    takes O(n) time.

    This data structure is conceptually related to binary search trees, which
    offer average O(log n) but worst-case O(n) time for search, insertion, and
    deletion, and to self-balancing binary search trees, which offer average
    and worst-case O(log n) time for search, insertion, and deletion. Trees
    overcome the need to perform linearily many moves to insert in the middle.
    The Python standard library has no BST. This project doesn't either, yet.

    NOTE: This is not "flat" in the sense of flat collections in Python. Those
    are collections like str and bytes that aren't containers: their elements
    aren't objects, just values stored contiguously in the collection's memory.
    """

    __slots__ = ('_entries',)

    def __init__(self, other=()):
        """Make a sorted flat table, optionally from a mapping or iterable."""
        self._entries = []
        self.update(other)

    def __len__(self):
        """How many key-value pairs are in this sorted flat table."""
        return len(self._entries)

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        _, entry = self._search(key)
        if entry is None:
            raise KeyError(key)
        return entry.value

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        index, entry = self._search(key)
        if entry is None:
            self._entries.insert(index, _Entry(key, value))
        else:
            entry.value = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key is mapped to no value."""
        index, entry = self._search(key)
        if entry is None:
            raise KeyError(key)
        del self._entries[index]

    def __iter__(self):
        """Iterate through the keys of this sorted flat table."""
        return (entry.key for entry in self._entries)

    def clear(self):
        """Remove all items from this sorted flat table."""
        self._entries.clear()

    def _search(self, key):
        """Find the insertion point and, if any, existing entry for a key."""
        index = bisect.bisect_left(self._entries, key,
                                   key=operator.attrgetter('key'))

        if index < len(self):
            entry = self._entries[index]
            assert not entry.key < key, 'bisection gave wrong result'
            if not key < entry.key:
                return index, entry

        return index, None


class UnsortedFlatTable(_NiceReprMapping, MutableMapping):
    """
    A mutable mapping storing entries unordered in a non-nested sequence.

    Keys may be compared with "is", "is not", "==", and "!=", and have their
    prehashes computed with the hash builtin. They need not support any other
    operations. To match the behavior of dict, keys that are the same object
    are regarded to be the same key, even if they are pathologically unequal to
    themselves. This is mainly to allow math.nan and other floating-point NaNs,
    the only reasonable uses of non-reflexive equality comparison. Keys mustn't
    exhibit other pathological equality comparison behavior. For example, "=="
    must be symmetric and transitive, and "!=" must give the opposite result.

    Searching takes O(n) average and worst-case time. Inserting and deleting
    take O(n) as well, because a search is performed first, to do them. As an
    implementation detail, they do only O(1) work in addition to that search.
    Iterating through all items takes O(n) time.

    This data structure is conceptually related to hash tables, which offer
    amortized O(1) search, insertion, and deletion with high probability,
    assuming good hash distribution. Hash tables overcome the need to examine
    linearily many entries to find a match, by using keys' hashes to know
    roughly where to look. dict is a hash table, as is HashTable below.

    NOTE: See the explanation in SortedFlatTable on different senses of "flat".
    """

    __slots__ = ('_entries',)

    def __init__(self, other=()):
        """
        Make an unsorted flat table, optionally from a mapping or iterable.
        """
        self._entries = []
        self.update(other)

    def __len__(self):
        """How many key-value pairs are in this unsorted flat table."""
        return len(self._entries)

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        try:
            _, entry = self._search(key)
        except StopIteration:
            raise KeyError(key) from None

        return entry.value

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        try:
            _, entry = self._search(key)
        except StopIteration:
            self._entries.append(_Entry(key, value))
        else:
            entry.value = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key is mapped to no value."""
        try:
            index, _ = self._search(key)
        except StopIteration:
            raise KeyError(key) from None

        self._entries[index] = self._entries[-1]
        del self._entries[-1]

    def __iter__(self):
        """Iterate through the keys of this unsorted flat table."""
        return (entry.key for entry in self._entries)

    def clear(self):
        """Remove all items from this unsorted flat table."""
        self._entries.clear()

    def _search(self, key):
        """Find the index and entry for a given key, or raise StopIteration."""
        return next((index, entry) for index, entry in enumerate(self._entries)
                    if entry.key is key or entry.key == key)


class DirectAddressTable(MutableMapping):
    """
    A direct address table. Lookups are directly achieved by sequence indexing.

    This is the simplest kind of explicit mapping, of those with constant-time
    operations. Search, insertion, and deletion are all O(1). But with a
    capacity of m, keys must be nonnegative integers less than m, and space
    usage is always Θ(m). (Table creation thus also takes Ω(m) time.) Iterating
    through all n items also takes Θ(m) time, even if n is much smaller than m.

    This is the immediate conceptual precursor to a hash-based container, and
    technically constitutes the simplest case of perfect (i.e., collision-free)
    hashing. In a direct address table, every key "hashes" to itself.
    """

    __slots__ = ('_values', '_len')

    _absent = object()
    """Sentinel representing the absence of an entry."""

    def __init__(self, capacity, other=()):
        """
        Create a direct address table allowing keys k where 0 <= k < capacity.

        A mapping, or an iterable of (key, value) pairs, may also be passed to
        supply initial items for the table.
        """
        if not isinstance(capacity, int):
            typename = type(capacity).__name__
            raise TypeError(f'capacity must be int, not {typename}')
        if capacity < 0:
            raise ValueError(f'capacity cannot be negative')
        self._values = [self._absent] * capacity
        self._len = 0
        self.update(other)

    def __repr__(self):
        """Python code representation of this direct address table."""
        item_strings = (f'{key!r}: {value!r}' for key, value in self.items())
        dict_repr = '{%s}' % ", ".join(item_strings)
        return f'{type(self).__name__}({self.capacity!r}, {dict_repr})'

    def __len__(self):
        """How many key-value pairs are in this direct address table."""
        return self._len

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        self._check_key(key)
        value = self._values[key]
        if value is self._absent:
            raise KeyError(key)
        return self._values

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        self._check_key(key)
        if self._values[key] is self._absent:
            self._len += 1
        self._values[key] = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key is mapped to no value."""
        self._check_key(key)
        if self._values[key] is self._absent:
            raise KeyError(key)
        self._values[key] = self._absent
        self._len -= 1

    def __iter__(self):
        """Iterate through the keys of this direct address table."""
        return (key for key, value in enumerate(self._values)
                if value is not self._absent)

    @property
    def key_range(self):
        """The range of allowed keys."""
        return range(len(self._values))

    def _check_key(self, key):
        """Raise an appropriate exception if a key cannot be used."""
        if not isinstance(key, int):
            raise TypeError(f'key must be int, not {type(key).__name__}')
        if not 0 <= key < self.capacity:
            raise ValueError(f'key must be in range({self.capacity})')


class HashTable(_NiceReprMapping, MutableMapping):
    """
    Hash-based mutable mapping. Like dict but with no order guarantees.

    Both dict and this class are hash tables. The dissimilar name HashTable is
    not to distinguish this in a technical way from other hash-based mappings
    like dict, just to avoid name confusion or a false appearance that this and
    dict have all the same methods and guarantees or are implemented similarly.

    This uses separate chaining (open hashing, closed addressing) to resolve
    collisions, while dict (in CPython) uses open addressing (closed hashing).

    Unlike dict, this doesn't preserve insertion order: iterating through a
    HashTable may yield items in any order. At a high level of abstraction,
    that distinction is unrelated to separate chaining vs. open addressing. (In
    general, neither approach is sufficient to achieve order preservation.)

    Like dict, this treats keys that are the same object as the same key, even
    if pathologically unequal to themselves. See UnsortedFlatTable for details.

    Search, insertion, and deletion all take amortized worst-case O(1) time
    with high probability, assuming good hash distribution. This situation is
    usually described as simply "O(1)", including elsewhere in this project.
    But the operations' non-amortized times are average O(1), worst-case O(n).
    Iterating through all items takes O(n) time, so [FIXME: say what's needed].
    """

    __slots__ = ('_buckets', '_len')

    _MIN_BUCKETS = 8
    """The bucket count never drops below this, even in empty tables."""

    _SHRINK_THRESHOLD = 0.25
    """The load factor below which the bucket count may be decreased.."""

    _GROW_THRESHOLD = 0.75
    """The load factor above which the bucket count may be increased."""

    _REHASH_LOAD_FACTOR = 0.5
    """The target load factor after rehashing to change the bucket count."""

    # These should be fairly far apart, but this just checks they make sense.
    assert _SHRINK_THRESHOLD < _REHASH_LOAD_FACTOR < _GROW_THRESHOLD

    @classmethod
    def fromkeys(cls, iterable, value=None):
        """Make a hash table from an iterable of keys, all mapped to value."""
        return cls((key, value) for key in iterable)

    def __init__(self, other=()):
        """Make a hash table, optionally from a mapping or iterable of items."""
        self.clear()
        self.update(other)

    def __len__(self):
        """How many key-value pairs are in this hash table."""
        return self._len

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        _, _, entry = self._search(key)
        if entry is None:
            raise KeyError(key)
        return entry.value

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        bucket, _, entry = self._search(key)
        if entry is None:
            bucket.append(_Entry(key, value))
            self._len += 1
            self._maybe_grow()
        else:
            entry.value = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key maps to no value."""
        bucket, index, _ = self._search(key)
        if index is None:
            raise KeyError(key)
        bucket[index] = bucket[-1]
        del bucket[-1]
        self._len -= 1
        self._maybe_shrink()

    def __iter__(self):
        """Iterate through the keys of this hash table."""
        return (entry.key for entry in self._entries)

    def clear(self):
        """Remove all items from this hash table."""
        self._buckets = [[] for _ in range(self._MIN_BUCKETS)]
        self._len = 0

    @property
    def _load_factor(self):
        """Ratio of number of entries to number of buckets."""
        return len(self) / len(self._buckets)

    @property
    def _target_bucket_count(self):
        """Estimated number of of buckets ideal for the current load."""
        return len(self) / self._REHASH_LOAD_FACTOR

    @property
    def _entries(self):
        """An iterator to all entries in this hash table."""
        return itertools.chain.from_iterable(self._buckets)

    def _search(self, key):
        """Find the bucket and, if any, index and entry for a key."""
        bucket = self._buckets[hash(key) % len(self._buckets)]
        try:
            index, entry = next((i, e) for i, e in enumerate(bucket)
                                if e.key is key or e.key == key)
        except StopIteration:
            index = entry = None
        return bucket, index, entry

    def _rehash(self, new_bucket_count):
        """Rebuild the hash table to have the given number of buckets."""
        new_buckets = [[] for _ in range(new_bucket_count)]
        for entry in self._entries:
            new_buckets[hash(entry.key) % new_bucket_count].append(entry)
        self._buckets = new_buckets

    def _maybe_grow(self):
        """Rehash for more buckets if the load factor is high."""
        if self._load_factor > self._GROW_THRESHOLD:
            self._rehash(math.ceil(self._target_bucket_count))

    def _maybe_shrink(self):
        """Rehash for fewer buckets if the load factor is low and we can."""
        if self._load_factor < self._SHRINK_THRESHOLD:
            new_bucket_count = max(self._MIN_BUCKETS,
                                   math.floor(self._target_bucket_count))
            if new_bucket_count < len(self._buckets):
                self._rehash(new_bucket_count)
