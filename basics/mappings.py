"""
Simple, BST-based, and hash-based mutable mappings.

Much as sequences.Vec uses inherited MutableSequence mixins, mappings in this
module use MutableMapping mixins where appropriate. But they override instead
whenever it improves asymptotic time complexity, and may do so to gain constant
factor speedup when simple and straightforward to achieve. Particular attention
is given to the keys, items, and values methods, whose default implementations
only perform acceptably if indexing takes O(1) or amortized O(1) time.

The point of these mappings is to be their own data structures. So they should
not delegate to a standard library mapping such as dict. But dict is all over
the place in Python and can't always be avoided. The following uses are exempt:

  1. Module and class dictionaries, in ordinary attribute and variable access.

  2. Graphviz drawing, behind the scenes or to set graph/node/edge attributes.

  3. Construction from arbitrarily named keyword arguments. No type in this
     module requires that it be constructible that way, but if you want to
     allow it, the dict shouldn't stop you. Functions (including methods) that
     construct a mapping from key-value pairs passed as keyword arguments may
     delegate to other such functions, and to functions that don't accept
     arbitrary keyword arguments. But other forms of construction may not make
     use of such a function.

  4. Equality comparison, under specific circumstances. Comparing instances of
     the same public mapping type in this module must NOT create any dict. This
     includes instances of future subclasses that don't inherit from each other
     (though if a subclass author further customizes equality comparison, code
     in this module is not responsible for that custom behavior). The __eq__
     method inherited from collections.abc.Mapping converts its operands' items
     views to dict and compares the dicts. Calling that implementation through
     a super proxy is an exempt use of dict, if not done with direct or
     indirect instances of the same public mapping type in this module. This is
     to allow you to fall back to that method for comparisons conceptually
     outside the purpose of your code. It also occasionally confers a
     performance advantage over direct equality comparison of items views.

  5. BinarySearchTree._check_ri, and any other _check_ri methods with the same
     meaning and usage if you choose to write them in other classes, are
     completely exempt. (But it won't necessarily help to use dict in them.)

It follows that mapping and mapping view instances from code in this module
have no instance dictionaries, because instance dictionaries are not listed as
exempt. That reprs, if evaluated, create a dict and pass it to a constructor,
requires no exemption, since no code in this module should run a repr as code.
But these reprs must not be produced by creating a dict and calling repr on it.

NOTE: I suggest first implementing of some or all types in this module with the
default mapping views (i.e., without overriding keys, items, or values), even
if asymptotically too slow; without reversibility (i.e., without implementing
__reversed__), even though meaningfully ordered mappings and their views ought
to be reversible; and without customizing equality comparison, even though
collections.abc.Mapping.__eq__ converts all items views to dict. After you
design and implement other functionality, you can devise an elegant approach to
these issues, avoiding duplicate logic. If you choose to proceed this way, make
this note a fixme. Once all requirements are met, remove this note entirely.
"""

from abc import abstractmethod
import bisect
from collections.abc import (
    ItemsView,
    KeysView,
    Mapping,
    MappingView,
    MutableMapping,
    ValuesView,
)
import html
import itertools
import logging
import math
import operator

import graphviz


def _reverse_enumerate(elements):
    """Enumerate a sized reversible iterable from high to low indexed items."""
    return zip(range(len(elements) - 1, -1, -1), reversed(elements))


def _fromkeys_named_constructor(cls):
    """Decorator defining the fromkeys named constructor for a mapping."""
    @classmethod
    def fromkeys(cls, iterable, value=None):
        """Make a mapping from an iterable of keys, all mapped to value."""
        return cls((key, value) for key in iterable)

    cls.fromkeys = fromkeys
    return cls


def _nice_repr(cls):
    """Decorator defining a mapping's repr to show construction from a dict."""
    def __repr__(self):
        """Python code representation of this mapping."""
        item_strings = (f'{key!r}: {value!r}' for key, value in self.items())
        dict_repr = '{%s}' % ", ".join(item_strings)
        return f'{type(self).__name__}({dict_repr})'

    cls.__repr__ = __repr__
    return cls


def _unordered_equality(cls):
    """Decorator defining unordered __eq__ for similarly typed mappings."""
    def __eq__(self, other):
        """Check if two mappings have equal keys and corresponding values."""
        if not isinstance(other, cls):
            return super(cls, self).__eq__(other)

        # Items view equality uses Set equality, which checks sizes before
        # comparing elements (see collections.abc.Set.__eq__), so comparing
        # items views of unequal size takes O(1) time.
        return self.items() == other.items()

    cls.__eq__ = __eq__
    return cls


def _ordered_equality(cls):
    """Decorator defining ordered __eq__ for similarly typed mappings."""
    def __eq__(self, other):
        """Check if two mappings have equal keys and corresponding values."""
        if not isinstance(other, SortedFlatTable):
            return super(cls, self).__eq__(other)

        # This is necessary before zipping and comparing, as one operand may
        # have more items than the other. Then, without this, some items would
        # be ignored and True could be wrongly returned. This also is needed to
        # make it so unequal-size comparisons always take O(1) time.
        if len(self) != len(other):
            return False

        return all(not (lhs_key < rhs_key or rhs_key < lhs_key)
                   and (lhs_value is rhs_value or lhs_value == rhs_value)
                   for (lhs_key, lhs_value), (rhs_key, rhs_value)
                   in zip(self.items(), other.items()))

    cls.__eq__ = __eq__
    return cls


class _Entry:
    """A key-value pair."""

    __slots__ = ('key', 'value')

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.key!r}, {self.value!r})'


class _FastIteratingMapping(Mapping):
    """
    ABC for mappings with efficient views and forward iteration.

    The items and values methods of collections.abc.Mapping return views that
    iterate through the mapping's keys and index the mapping with each key to
    obtain their values. In mapping types whose __getitem__ method takes O(1)
    or amortized O(1) time, this is usually reasonable. Otherwise, it will be
    too slow. The chief purpose of this base class is to handle those cases.

    The _KeysView, _ValuesView, and _ItemsView classes and _items method are
    protected. Only code in this and derived classes may override or use them.
    """

    __slots__ = ()

    _KeysView = KeysView

    class _ItemsView(ItemsView):
        """Efficiently iterable view of the items of a mapping."""

        __slots__ = ()

        def __iter__(self):
            """Iterate efficiently though the (key, value) pairs."""
            return self._mapping._items()

    @ValuesView.register  # Don't want collections.abc.ValuesView.__contains__.
    class _ValuesView(MappingView):
        """Efficiently iterable view of the values of a mapping."""

        __slots__ = ()

        # Don't need __contains__. We want the default "in" logic of iterables.

        def __iter__(self):
            """Iterate efficiently through the values."""
            return (value for _, value in self._mapping._items())

    def __iter__(self):
        """Iterate efficiently through the keys."""
        return (key for key, _ in self._items())

    def keys(self):
        """Get an efficiently iterable view of the keys."""
        return self._KeysView(self)

    def items(self):
        """Get an efficiently iterable view of the (key, value) pairs."""
        return self._ItemsView(self)

    def values(self):
        """Get an efficiently iterable view of the values."""
        return self._ValuesView(self)

    @abstractmethod
    def _items(self):
        """
        Yield all (key, value) pairs, efficiently and in some acceptable order.

        A derived class must override this protected method to provide the
        iteration logic that __iter__ and all three mapping views will use.
        """
        raise NotImplementedError


class _FastIteratingReversibleMapping(_FastIteratingMapping):
    """ABC for reversible mappings with efficient views and iteration."""

    __slots__ = ()

    class _KeysView(KeysView):
        """Efficiently iterable reversible view of the keys of a mapping."""

        __slots__ = ()

        def __reversed__(self):
            """Iterate efficiently through the the keys in reverse order."""
            return reversed(self._mapping)

    class _ItemsView(_FastIteratingMapping._ItemsView):
        """Efficiently iterable reversible view of the items of a mapping."""

        __slots__ = ()

        def __reversed__(self):
            """
            Iterate efficiently though the (key, value) pairs in reverse order.
            """
            return self._mapping._reversed_items()

    class _ValuesView(_FastIteratingMapping._ValuesView):
        """Efficiently iterable reversible view of the values of a mapping."""

        __slots__ = ()

        def __reversed__(self):
            """Iterate efficiently through the values in reverse order."""
            return (value for _, value in self._mapping._reversed_items())

    def __reversed__(self):
        """Iterate efficiently through the keys, in reverse order."""
        return (key for key, _ in self._reversed_items())

    @abstractmethod
    def _reversed_items(self):
        """
        Yield all (key, value) pairs efficiently, in reverse order.

        A derived class must override this protected method to provide the
        iteration logic that __iter__ and all three mapping views will use.
        """
        raise NotImplementedError


@_unordered_equality
@_nice_repr
@_fromkeys_named_constructor
class UnsortedFlatTable(_FastIteratingMapping, MutableMapping):
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
    Iterating through all items takes O(n) time. Since keys need neither be
    hashable nor order comparable, it takes O(n**2) time to check if
    UnsortedFlatTable instances are equal, but O(1) when their sizes differ.

    This data structure is conceptually related to hash tables, which offer
    amortized O(1) search, insertion, and deletion with high probability,
    assuming good hash distribution. Hash tables overcome the need to examine
    linearily many entries to find a match, by using keys' hashes to know
    roughly where to look. dict is a hash table, as is HashTable below.

    NOTE: This is not "flat" in the sense of flat collections in Python. Those
    are collections like str and bytes whose elements aren't their own objects,
    just values stored contiguously in the collection's memory.
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

    def clear(self):
        """Remove all items from this unsorted flat table."""
        self._entries.clear()

    def _items(self):
        return ((entry.key, entry.value) for entry in self._entries)

    def _search(self, key):
        """Find the index and entry for a given key, or raise StopIteration."""
        return next((index, entry) for index, entry in enumerate(self._entries)
                    if entry.key is key or entry.key == key)


@_ordered_equality
@_nice_repr
@_fromkeys_named_constructor
class SortedFlatTable(_FastIteratingReversibleMapping, MutableMapping):
    """
    A mutable mapping storing entries, sorted by key, in a non-nested sequence.

    All keys must be comparable by "<" and ">". The "==", "!=", "<=", and ">="
    operators will not be used to compare keys. Keys that are neither less nor
    greater than one another are regarded to be the same key, and keys must at
    least have a weak ordering. For example, using (arbitrary) sets as keys
    doesn't work, since the partial ordering of subsets is not a weak ordering.
    No special support is provided for pathological objects like math.nan as
    keys. But in the few cases values are compared, such objects are supported.

    Searching takes O(log n) average and worst-case time. Inserting and
    deleting take O(n) average and worst-case time. Iterating through all items
    takes O(n) time. It takes O(n) time to check if SortedFlatTable instances
    are equal, but O(1) when their sizes differ.

    This data structure is conceptually related to binary search trees, which
    offer average O(log n) but worst-case O(n) time for search, insertion, and
    deletion, and to self-balancing binary search trees, which offer average
    and worst-case O(log n) time for search, insertion, and deletion. Trees
    overcome the need to perform linearily many moves to insert in the middle.
    The Python standard library has no BST. The BinarySearchTree class below is
    a BST, but not self-balancing. This project has no self-balancing BST yet.

    NOTE: See explanation in UnsortedFlatTable on different senses of "flat".
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

    def clear(self):
        """Remove all items from this sorted flat table."""
        self._entries.clear()

    def _items(self):
        return ((entry.key, entry.value) for entry in self._entries)

    def _reversed_items(self):
        return ((entry.key, entry.value) for entry in reversed(self._entries))

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


class _Node:
    """A node in a binary search tree with parent pointers."""

    __slots__ = ('parent', 'left', 'right', 'key', 'value')

    def __init__(self, parent, left, right, key, value):
        """Create a new BST node."""
        self.parent = parent
        self.left = left
        self.right = right
        self.key = key
        self.value = value

    def __repr__(self):
        """Representation for debugging."""
        parent_text = f'@0x{id(self.parent):X}' if self.parent else '=None'

        return (f'<{type(self).__name__}@0x{id(self):X} parent{parent_text}'
                f' left={self.left!r} right={self.right!r}'
                f' key={self.key!r} value={self.value!r}>')


# !!FIXME: When removing implementation bodies, keep skeletons for draw, _min,
#          _next, and _check_ri, but show _min and _next as instance methods.
@_ordered_equality
@_nice_repr
@_fromkeys_named_constructor
class BinarySearchTree(_FastIteratingReversibleMapping, MutableMapping):
    """
    A mutable mapping implemented as a non-self-balancing binary search tree.

    Search, insertion, and deletion take time linear in the height of the tree:
    O(log n) on average, but O(n) in the worst case. This has better average
    case asymptotic performance than SortedFlatTable because it doesn't have to
    move elements; the number of keys greater or less than a key to be inserted
    or deleted is thus typically irrelevant. Iterating through all items takes
    O(n) time. It takes O(n) time to check if BinarySearchTree instances are
    equal, but O(1) when their sizes differ. No operators besides "<" and ">"
    are used to compare keys.

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

    Other significant implementation details: Insertion adds leaves; paths from
    the root to preexisting nodes are unchanged. Deleting a node must sometimes
    alter the structure of one of its subtrees, but paths from the root of the
    whole tree to nodes outside the subtree rooted by the deleted node are
    unchanged. Deletion is the trickiest operation; it must be divided into
    several cases. The private _min and _next methods are of great importance.
    """

    __slots__ = ('_root', '_len', '_debug')

    def __init__(self, other=(), *, debug=False):
        """Make a BST, optionally from a mapping or iterable of items."""
        if debug:
            logging.warn('%s@0x%X in debug mode, expect slow operations',
                         type(self).__name__, id(self))
        self._debug = debug
        self.clear()
        self.update(other)

    def __len__(self):
        """How many key-value pairs are in this BST."""
        return self._len

    def __getitem__(self, key):
        """Get the value stored at a given key."""
        _, child = self._search(key)
        if not child:
            raise KeyError(key)
        return child.value

    def __setitem__(self, key, value):
        """Create or replace a value to be stored at a given key."""
        parent, child = self._search(key)

        if child:
            child.value = value
        else:
            self._insert(parent, key, value)
            self._len += 1

        self._maybe_check_ri()

    def __delitem__(self, key):
        """Remove a value at a given key, so the key maps to no value."""
        _, child = self._search(key)
        if not child:
            raise KeyError(key)
        self._delete(child)
        self._len -= 1
        self._maybe_check_ri()

    def clear(self):
        """Remove all items from this BST."""
        self._root = None
        self._len = 0
        self._maybe_check_ri()

    def draw(self, *, check_ri=True):
        """
        Draw the tree as a graphviz.Digraph.

        Drawings are similar to those by tree.draw and tree.draw_iterative, but
        not quite the same since nodes have key and value attributes, both of
        which are shown, rather than element attributes. Before any drawing,
        unless check_ri is False, the entire data structure is checked to
        ensure all representation invariants hold, and AssertionError is raised
        if not. As an implementation detail, the check is done by calling
        _check_ri (and the _check_ri docstring contains further explanation).
        To best safeguard against bugs, the traversal performed for drawing is
        carried out with different techniques from those _check_ri itself uses.
        """
        if check_ri:
            self._check_ri()

        graph = graphviz.Digraph()
        counter = itertools.count()
        stack = [(None, self._root)]

        while stack:
            parent_name, child = stack.pop()
            child_name = str(next(counter))

            if child:
                key_text = html.escape(repr(child.key))
                value_text = html.escape(repr(child.value))
                graph.node(child_name, label=f'{key_text} &rarr; {value_text}')
                stack.append((child_name, child.right))
                stack.append((child_name, child.left))
            else:
                graph.node(child_name, shape='point')

            if parent_name is not None:
                graph.edge(parent_name, child_name)

        return graph

    def _items(self):
        """
        Yield all (key, value) pairs in O(n) time, in ascending order.

        This is a left-to-right inorder traversal of the tree.
        """
        node = self._min(self._root)
        while node:
            yield node.key, node.value
            node = self._next(node)

    def _reversed_items(self):
        """
        Yield all (key, value) pairs in O(n) time, in descending order.

        This is a right-to-left inorder traversal of the tree.
        """
        node = self._max(self._root)
        while node:
            yield node.key, node.value
            node = self._prev(node)

    @staticmethod
    def _min(node):
        """
        Get the first node in inorder traversal under node, nor None if None.

        For some subtrees, this is node itself.

        This important private method takes time linear in the height of the
        tree (more specifically, the height of the subtree) in the worst case.
        """
        if not node:
            return None

        while node.left:
            node = node.left

        return node

    @staticmethod
    def _max(node):
        """
        Get the last node in inorder traversal under node, or None if None.

        Details in _min apply to this as well, including time complexity.
        """
        if not node:
            return None

        while node.right:
            node = node.right

        return node

    @classmethod
    def _next(cls, node):
        """
        Get node's successor in inorder traversal, or None if node comes last.

        The successor of node may or may not be in the subtree rooted at node.

        This very important private method takes time linear in the height of
        the tree in the worst case, but its average running time over all nodes
        of any tree of any height is O(1).
        """
        if not node:
            return None

        if node.right:
            return cls._min(node.right)

        while node.parent:
            if node is node.parent.left:
                return node.parent
            assert node is node.parent.right
            node = node.parent

        return None

    @classmethod
    def _prev(cls, node):
        """
        Get node's predecessor in inorder traversal, or None if node comes
        first.

        Details in _next apply to this as well, including time complexity.
        """
        if not node:
            return None

        if node.left:
            return cls._max(node.left)

        while node.parent:
            if node is node.parent.right:
                return node.parent
            assert node is node.parent.left
            node = node.parent

        return None

    def _search(self, key):
        """
        Find an the insertion point for a key in the tree.

        This returns a tuple: the parent node that has or would have a node for
        key as one of its children, or None if there is no parent; and the
        child node whose key is similar to key key, or None if there isn't one.
        """
        parent = None
        child = self._root

        while child:
            if key < child.key:
                parent = child
                child = child.left
            elif child.key < key:
                parent = child
                child = child.right
            else:
                break

        return parent, child

    def _insert(self, parent, key, value):
        """Insert a new (key, value) node as a child of the given parent."""
        child = _Node(parent, None, None, key, value)

        if not parent:
            assert not self._root
            self._root = child
        elif key < parent.key:
            assert not parent.left
            parent.left = child
        else:
            assert parent.key < key
            assert not parent.right
            parent.right = child

    def _delete(self, node):
        """Delete the given node and update the tree appropriately."""
        parent = node.parent
        replacement = self._do_delete(node)

        if not parent:
            assert node is self._root
            self._root = replacement
        elif node is parent.left:
            parent.left = replacement
        else:
            assert node is parent.right
            parent.right = replacement

        if replacement:
            replacement.parent = parent

        node.parent = node.left = node.right = None

    @classmethod
    def _do_delete(cls, node):
        """Delete the given node and return the new root of its subtree."""
        # Case 1: No children.
        if not (node.left or node.right):
            return None

        # Case 2: One child.
        if not node.right:
            return node.left
        if not node.left:
            return node.right

        # Case 3: Two children, right child is the minimum in its subtree.
        if not node.right.left:
            node.left.parent = node.right
            node.right.left = node.left
            return node.right

        # Case 4: Two children, right child is not the minimum of its subtree.

        replacement = cls._min(node.right.left)
        assert not replacement.left

        # Splice the new subroot out of its original place in the right branch.
        assert replacement is replacement.parent.left
        replacement.parent.left = replacement.right
        if replacement.right:
            replacement.right.parent = replacement.parent

        # Attach both left and right branches to the new subroot.
        replacement.left = node.left
        node.left.parent = replacement
        replacement.right = node.right
        node.right.parent = replacement

        return replacement

    def _maybe_check_ri(self):
        """Check representation invariants if _debug is true."""
        if self._debug:
            self._check_ri()

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
        if not __debug__:
            logging.warn('%s@0x%X _check_ri ineffective: interpreter has -O',
                         type(self).__name__, id(self))

        if not self:
            assert self._len == 0
            assert self._root is None
            return

        assert self._len > 0
        assert self._root is not None
        assert self._root.parent is None

        unbounded = object()

        def check_and_count(node, lower, upper):
            assert isinstance(node, _Node)

            if lower is not unbounded:
                assert lower < node.key
            if upper is not unbounded:
                assert node.key < upper

            count = 1

            if node.left is not None:
                assert node.left.parent is node
                count += check_and_count(node.left, lower, node.key)

            if node.right is not None:
                assert node.right.parent is node
                count += check_and_count(node.right, node.key, upper)

            return count

        total_count = check_and_count(self._root, unbounded, unbounded)
        assert total_count == len(self)


@_ordered_equality
class DirectAddressTable(_FastIteratingReversibleMapping, MutableMapping):
    """
    A direct address table. Lookups are directly achieved by sequence indexing.

    This is the simplest kind of explicit mapping, of those with constant-time
    operations. Search, insertion, and deletion are all O(1). But with a
    capacity of m, keys must be nonnegative integers less than m, and space
    usage is always Θ(m). (Table creation thus also takes Ω(m) time.) Iterating
    through all n items also takes Θ(m) time, even if n is much smaller than m.
    It takes O(n) time to check if DirectAddressTable instances are equal, but
    O(1) when their sizes differ.

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
            raise TypeError(f"capacity must be 'int', not {typename!r}")
        if capacity < 0:
            raise ValueError(f'capacity cannot be negative, got {capacity!r}')
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

    @property
    def capacity(self):
        """The number of distinct possible keys."""
        return len(self._values)

    def _items(self):
        return self._items_by(enumerate)

    def _reversed_items(self):
        return self._items_by(_reverse_enumerate)

    def _check_key(self, key):
        """Raise an appropriate exception if a key cannot be used."""
        if not isinstance(key, int):
            raise TypeError(f"key must be 'int', not {type(key).__name__!r}")
        if not 0 <= key < self.capacity:
            raise ValueError(f'key must be in range({self.capacity!r})')

    def _items_by(self, enumerator):
        """Helper function for _items and _reversed_items."""
        return ((key, value) for key, value in enumerator(self._values)
                if value is not self._ABSENT)


@_unordered_equality
@_nice_repr
@_fromkeys_named_constructor
class HashTable(_FastIteratingMapping, MutableMapping):
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
    affect the design. Do this before writing any code of the class.] It takes
    O(n) time to check if HashTable instances are equal, but O(1) when their
    sizes differ.

    [FIXME: Make a PythonTutor demo of HashTable and give the permalink here.]
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

    def __init__(self, other=()):
        """
        Make a hash table, optionally from a mapping or iterable of items.
        """
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

    def clear(self):
        """Remove all items from this hash table."""
        self._buckets = [[] for _ in range(self._MIN_BUCKETS)]
        self._len = 0

    def _items(self):
        return ((entry.key, entry.value) for entry in self._entries)

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


__all__ = [thing.__name__ for thing in (
    UnsortedFlatTable,
    SortedFlatTable,
    BinarySearchTree,
    DirectAddressTable,
    HashTable,
)]
