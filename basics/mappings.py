"""Simple, BST-based, and hash-based mutable mappings."""

import bisect
from collections.abc import Mapping, MutableMapping
import itertools
import math
import operator


def _reverse_enumerate(elements):
    """Enumerate a sized reversible iterable from high to low indexed items."""
    return zip(range(len(elements) - 1, -1, -1), reversed(elements))


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
    The Python standard library has no BST. The BinarySearchTree class below is
    a BST, but not self-balancing. This project has no self-balancing BST yet.

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

    def __reversed__(self):  # FIXME: Make all 3 mapping views reversible too.
        """Iterate in reverse through the keys of this sorted flat table."""
        return (entry.key for entry in reversed(self._entries))

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

    Keys may be compared by "is", "is not", "==", and "!=". They need not
    support other operations. To match the behavior of dict, keys that are the
    same object are regarded to be the same key, even if pathologically unequal
    to themselves. This is mainly to allow math.nan and other floating-point
    NaNs, the only reasonable uses of non-reflexive equality comparison. Keys
    mustn't exhibit other pathological equality comparison behavior (e.g., "=="
    must be symmetric and transitive, and "!=" must give the opposite result).

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


# !!FIXME: When removing implementation bodies, leave the _successor and
#          _check_ri methods' headers ("def" lines) and docstrings.
class BinarySearchTree(_NiceReprMapping, MutableMapping):
    """
    A mutable mapping implemented as a non-self-balancing binary search tree.

    Search, insertion, and deletion take time linear in the height of the tree:
    O(log n) on average, but O(n) in the worst case. This has better average
    case asymptotic performance than SortedFlatTable because it doesn't have to
    move elements; the number of keys greater or less than a key to be inserted
    or deleted is thus typically irrelevant. Iterating through all elements
    takes O(n) time. No operators besides "<" and ">" are used to compare keys.

    The same keys can be arranged in BSTs of different structures. Most such
    structures are balanced or nearly balanced, but some are not. Production
    quality general purpose BST-based sets and mappings carry out "rotations"
    to rearrange trees' structures to keep them sufficiently balanced to ensure
    O(log n) height. For simplicity, this class does not. Inserting keys in
    random order gives O(log n) height with high probability. Unfortunately,
    when keys are inserted in sorted or reverse sorted order, which are common
    in practice, the tree is unbalanced. Self-balancing BST (e.g., red-black
    tree or AVL tree) mapping types may be added to this module in the future.

    The draw method draws the tree, whose structure is otherwise considered an
    implementation detail. At all times, O(n) space is used, all but O(1) of
    which is nodes. Besides draw, public methods use O(1) auxiliary space. Read
    operations, such as indexing and iteration, write only to local variables.
    Achieving O(1) auxiliary space requires [FIXME: Say how this must affect
    the design. Do this before writing any code of the class.]
    """

    def _successor(self, node):
        """
        Return the node just after node in inorder traversal, or None.

        This very important private method takes time linear in the height of
        the tree in the worst case, but its average running time over all nodes
        of any tree of any height is O(1).
        """

    def _check_ri(self):
        """
        Check representation invariants, raising AssertionError on violation.

        This verifies all persistent state, including all attributes public
        methods rely on and all state accessible through them. For example, it
        ensures that this really is a BST and that the stored size is correct.

        Representation invariants are things guaranteed to be true of a data
        structure's underlying representation, at all times except during an
        operation that writes to the data structure. Operations that only read
        do not cause them to be violated even temporarily; writing operations
        may cause them to be violated temporarily but must always restore them.
        Representation invariants are your (justified) assumptions, as you code
        an operation. When you seek to prove a public method's implementation
        correct, representation invariants are available to you as premises.

        This supports a testing technique where mutating methods call _check_ri
        just before they are about to return, so that if there is a bug, it is
        most likely found quickly, unless _check_ri itself has a corresponding
        bug. To minimize the risk of that, _check_ri should avoid calling other
        methods (even private ones, unless they serve solely as helpers for
        _check_ri itself), and you may want to have it use algorithms and/or
        coding techniques that differ substantially from the rest of the class,
        especially if this also lets you make _check_ri simpler. It must read
        and verify all state associated with an instance, so it takes linear
        time. This is usually too slow, so _check_ri calls must be removed once
        the code is in good shape, but they can be restored for debugging. Or
        you can condition _check_ri calls on the value of a _debug attribute.

        Because the finished class will not (or not by default) call _check_ri,
        it need not obey auxiliary space complexity restrictions. Sometimes you
        can go further, including here: feel free to write _check_ri so that it
        fails with RecursionError on very deep trees, if you choose.
        """


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

    _ABSENT = object()
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
        self._values = [self._ABSENT] * capacity
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
        if value is self._ABSENT:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        self._check_key(key)
        if self._values[key] is self._ABSENT:
            self._len += 1
        self._values[key] = value

    def __delitem__(self, key):
        """Remove a value at a given key, so the key is mapped to no value."""
        self._check_key(key)
        if self._values[key] is self._ABSENT:
            raise KeyError(key)
        self._values[key] = self._ABSENT
        self._len -= 1

    def __iter__(self):
        """Iterate through the keys of this direct address table."""
        return (key for key, value in enumerate(self._values)
                if value is not self._ABSENT)

    def __reversed__(self):  # FIXME: Make all 3 mapping views reversible too.
        """Iterate in reverse through the keys of this direct address table."""
        return (key for key, value in _reverse_enumerate(self._values)
                if value is not self._ABSENT)

    @property
    def capacity(self):
        """The number of distinct possible keys."""
        return len(self._values)

    def _check_key(self, key):
        """Raise an appropriate exception if a key cannot be used."""
        if not isinstance(key, int):
            raise TypeError(f'key must be int, not {type(key).__name__}')
        if not 0 <= key < self.capacity:
            raise ValueError(f'key must be in range({self.capacity!r})')


class HashTable(_NiceReprMapping, MutableMapping):
    """
    Hash-based mutable mapping. Like dict but with no order guarantees.

    Both dict and this class are hash tables. The dissimilar name HashTable is
    not to distinguish this in a technical way from other hash-based mappings
    like dict, just to avoid name confusion or a false appearance that this and
    dict have all the same methods and guarantees or are implemented similarly.

    This uses separate chaining (open hashing, closed addressing) to resolve
    collisions, while dict (in CPython) uses open addressing (closed hashing).
    In separate chaining, buckets are sequences of zero or more entries, and
    collisions are resolved by searching the bucket (typically a sequential
    search). In open addressing, each bucket holds at most one entry, and
    collisions are resolved by choosing another bucket by following some rule
    that determines second, third, fourth, etc., choice bucket indices. An open
    addressing mapping type may be added to this module in the future.

    Unlike dict, this doesn't preserve insertion order: iterating through a
    HashTable may yield items in any order. At a high level of abstraction,
    that distinction is unrelated to separate chaining vs. open addressing. (In
    general, neither is sufficient to achieve order preservation.)

    Keys may be compared by "is", "is not", "==", and "!=", and have prehashes
    computed with the hash builtin. They need not support any other operations.
    Like dict, this treats keys that are the same object as the same key, even
    if pathologically unequal to themselves. See UnsortedFlatTable for details.

    Search, insertion, and deletion all take amortized worst-case O(1) time
    with high probability, assuming good hash distribution. This situation is
    usually described as simply "O(1)", including elsewhere in this project.
    But the operations' non-amortized times are average O(1), worst-case O(n).
    Iterating through all items takes O(n) time, so [FIXME: Say how this must
    affect the design. Do this before writing any code of the class.]
    """

    __slots__ = ('_buckets', '_len')

    _MIN_BUCKETS = 8
    """The bucket count never drops below this, even in empty tables."""

    _SHRINK_THRESHOLD = 0.25
    """The load factor below which the bucket count may be decreased."""

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


# !!FIXME: In addition to the changes described in the fixme below, I intend to
# omit this from the problem set that poses SortedFlatTable, UnsortedFlatTable,
# BinarySearchTree, DirectAddressTable, HashTable in this module, and various
# exercises in other modules. So GeneralOrderedMapping (hopefully with a better
# name) if present, make_ordered_mapping if still present, MyOrderedDict, and
# OrderedHashTable, will be removed for that. This should be done in a commit
# that makes no other changes, so that commit can be reverted later to finish
# developing these problems (or just to pose them, if already developed).
#
# !!FIXME: Although class factories are often good, here the design is inferior
# to having a GeneralOrderedMapping class that, when constructed, takes the
# underlying mutable mapping type by dependency injection, probably via a
# required keyword-only argument to __init__. Then one can directly instantiate
# GeneralOrderedMapping for one-off uses or, more often, inherit from it to
# bind that argument via a super() call in the derived class __init__. Then
# derived class metadata are correct automatically. (GeneralOrderedMapping
# would itself have no direct or indirect concrete base classes except object.)
#
# This exercise should either be changed to require that design, or a major
# subexercise should be added, calling for such a redesign. The former may be
# better, since the burdensome nature of the latter does not seem clearly
# justified. (There are other ways to have a class factory exercise.)
#
def make_ordered_mapping(mutable_mapping):
    """
    Create a new ordered mapping type based on a given mutable mapping type.

    This factory creates and returns a mutable mapping type, implemented in
    terms of mutable_mapping but not inheriting from it, that is ordered in
    the sense of satisfying all the following even if mutable_mapping doesn't:

      1. Iteration yields in insertion order. (Except per #4 below.)
      2. The reverse builtin gives an iterator going in the opposite order.
      3. Each call to next on either such iterator takes strictly O(1) time.
      4. A move_to_end method is provided, just as in collections.OrderedDict.

    This is to say that the relationship between mutable_mapping and
    make_ordered_mapping(mutable_mapping) is analogous to that between dict and
    OrderedDict, except composition is used instead of inheritance. Besides
    object, any direct or indirect base classes of types returned by
    make_ordered_mapping must be abstract.

    make_ordered_mapping(mutable_mapping) must support search, insertion, and
    removal with the same keys mutable_mapping supports, with the same time and
    space complexities, and the same exception types and messages on errors.
    Nothing may be assumed about the mechanism mutable_mapping uses to look up
    keys or what keys are valid. For example, keys in dict and HashTable must
    be hashable, and the basic operations all take O(1) amortized time with
    high probability assuming good hash distribution, so all that is true of
    make_ordered_mapping(dict) and make_ordered_mapping(HashTable), too. If you
    have a BST class that is a mutable mapping type based on a self-balancing
    binary search tree, its keys need not be hashable but must be comparable
    with "<" and be (at least) weakly ordered, and all basic operations take
    O(log n) time, so all that is true of make_ordered_mapping(BST), too.
    """
    # FIXME: Needs implementation.


# FIXME: Fix metadata, including adding docstring. Don't change implementation.
MyOrderedDict = make_ordered_mapping(dict)


# FIXME: Fix metadata, including adding docstring. Don't change implementation.
OrderedHashTable = make_ordered_mapping(HashTable)


# FIXME: After all tests of code in this module are passing, read the code of
# collections.OrderedDict and compare techniques with make_ordered_mapping.
