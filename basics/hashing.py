"""Mutable collections using hashing or similar techniques."""

from collections.abc import MutableMapping
import itertools
import math


class _Entry:
    """A key-value pair."""

    __slots__ = ('key', 'value')

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.key!r}, {self.value!r})'

    def matches(self, key):  # FIXME: Factor away uses of this and remove it.
        """Tell if this entry's key matches the given key."""
        return self.key is key or self.key == key


class SortedFlatTable(MutableMapping):
    """
    A mutable mapping storing entries, sorted by key, in a non-nested sequence.

    All keys must be comparable by "<" and ">". The "==", "!=", "<=", and ">="
    operators will not be used to compare keys. Keys that are neither less nor
    greater than one another are regarded to be the same key, and keys must at
    least have a weak ordering. For example, using (arbitrary) sets as keys
    doesn't work, since the partial ordering of subsets is not a weak ordering.
    No special support is provided for pathological objects like math.nan.

    Searching takes O(log n) average and worst-case time. Inserting and
    deleting take O(n) average and worst-case time.

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


class UnsortedFlatTable(MutableMapping):
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

    This data structure is conceptually related to hash tables, which offer
    amortized O(1) search, insertion, and deletion with high priority, assuming
    good hash distribution. Hash tables overcome the need to examine linearily
    many entries to find a match, by using keys' hashes to know roughly where
    to look. The built-in dict, and the HashTable class below, are hash tables.

    NOTE: See the explanation in SortedFlatTable on different senses of "flat".
    """


class DirectAddressTable(MutableMapping):
    """
    A direct address table. Lookups are directly achieved by sequence indexing.

    This is the simplest kind of explicit mapping, of those offering
    constant-time operations. Search, insertion, and deletion are all O(1).

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
        """The number of key-value pairs currently stored in this table."""
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

    @property
    def capacity(self):
        """The exclusive upper bound of the range of allowed keys."""
        return len(self._values)

    def _check_key(self, key):
        """Raise an appropriate exception if a key cannot be used."""
        if not isinstance(key, int):
            raise TypeError(f'key must be int, not {type(key).__name__}')
        if not 0 <= key < self.capacity:
            raise ValueError(f'key must be in range({self.capacity})')


class HashTable(MutableMapping):
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

    # These should really be FAR apart, but this just checks they are coherent.
    assert _SHRINK_THRESHOLD < _REHASH_LOAD_FACTOR < _GROW_THRESHOLD

    @classmethod
    def fromkeys(cls, iterable, value=None):
        """Make a hash table from an iterable of keys, all mapped to value."""
        return cls((key, value) for key in iterable)

    def __init__(self, other=()):
        """Make a hash table, optionally from a mapping or iterable of items."""
        self.clear()
        self.update(other)

    def __repr__(self):
        """Python code representation of this hash table."""
        item_strings = (f'{key!r}: {value!r}' for key, value in self.items())
        dict_repr = '{%s}' % ", ".join(item_strings)
        return f'{type(self).__name__}({dict_repr})'

    def __len__(self):
        """The number of key-value pairs currently stored in this hash table."""
        return self._len

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        bucket = self._get_bucket(key)
        try:
            return next(e.value for e in bucket if e.matches(key))
        except StopIteration:
            raise KeyError(key) from None

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        bucket = self._get_bucket(key)
        try:
            entry = next(e for e in bucket if e.matches(key))
        except StopIteration:
            bucket.append(_Entry(key, value))
            self._len += 1
            self._maybe_grow()
        else:
            entry.value = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key maps to no value."""
        bucket = self._get_bucket(key)
        try:
            index = next(i for i, e in enumerate(bucket) if e.matches(key))
        except StopIteration:
            raise KeyError(key) from None
        else:
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
