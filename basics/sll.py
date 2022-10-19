#!/usr/bin/env python

"""
Immutable singly linked lists using hash consing to share tails globally.

Hash consing is an advanced technique. This project currently has no module
dedicated to presenting singly linked lists in an introductory fashion. But a
basic use of singly linked lists, with no specialized techniques, appears in
queues.py, which contains an SLL-based FIFO queue and an SLL-based LIFO queue.

With hash consing--when global and guaranteed, as here--all SLLs that use the
hash-consed node type, existing at memory at any given time, form a single
"upside-down" tree. Its root (here, None) represents the empty sublist. Viewed
as part of this tree, next_node pointers are parent pointers. HashNode.draw()
illustrates this by building a graphviz.Digraph of the whole tree.

The HashNode type in this module uses reference-based equality comparison. But
HashNode-based SLLs always share the longest suffix possible. So if two
variables refer to heads of SLLs whose values are equal and in the same order,
those variables are guaranteed to refer to the same node object. That is, for
HashNode objects, reference equality is the same as structural equality (of the
linked lists they head). This is one of the benefits of hash consing.

Hash consing can be applied to any immutable node-based data structure whose
nodes make up a directed acyclic graph. This includes, but is not limited to,
binary and n-ary trees without parent pointers. This is analogous to the case
of singly linked lists. (A binary tree node has two child pointers; a singly
linked list node has one "child" pointer.) Only SLLs are implemented here.
"""

__all__ = ['HashNode', 'traverse']

import html
import threading
import weakref

import graphviz


class _Box:
    """
    Immutable weak-referenceable wrapper for the value held by a node.

    This is needed because:

    1. Nodes need to support elements without __weakref__, but we need element
       references from keys in the WeakValueTable to be weak to avoid leaking
       heterogeneous cycles.

    2. Floating-point NaNs are hashable but not equal even to themselves. To
       support them, standard library containers use both "==" and "is" in
       structural equality comparisons. HashNode does too, for consistency and
       to avoid creating duplicate nodes when an element is non-self-equal. But
       "==" between live weakref.ref objects compares the referents only with
       "==", not also "is". Wrapping each element in a _Box fixes that, too.

    Boxes are kept alive by strong references in nodes. WeakValueTable keys use
    weak references so heterogenous cycles through the table are never strong.
    """

    __slots__ = ('_value', '__weakref__')

    def __init__(self, value):
        """Create a box holding the given element value."""
        self._value = value

    def __repr__(self):
        """Python code representation for debugging."""
        return f'{type(self).__name__}({self.value!r})'

    def __eq__(self, other):
        """Boxes are equal when the objects they box are the same or equal."""
        if isinstance(other, self.__class__):
            return self.value is other.value or self.value == other.value
        return NotImplemented

    def __hash__(self):
        """A box hashes the same as its boxed object."""
        return hash(self.value)

    @property
    def value(self):
        """The element value held by this wrapper."""
        return self._value


class HashNode:
    """
    Immutable singly linked list node, using hash consing. Thread-safe.

    See the sll module docstring regarding the concepts involved. HashNode
    equality implies identity. Inheriting from this class is not recommended.
    Subclasses, if any, must carefully ensure all invariants are maintained.

    The uniqueness guarantee--that node equality implies identity--relies on
    each object ever used as an element being immutable, in the sense that its
    value never changes. Objects mutable (in that sense) shouldn't be hashable,
    so this restriction can only lead to problems in the presence of severe
    bugs in code outside this module: use of a hashable mutable type, or an
    encapsulation violation mutating an object considered immutable.

    Attempting to make a HashNode with a non-hashable element fails safely with
    TypeError, neither creating a HashNode nor corrupting shared state.

    HashNode is not hardened against resurrection. Weak reference callbacks are
    ideally called after the referent is [FIXME: write the rest].

    >>> head1 = HashNode('a', HashNode('b', HashNode('c', HashNode('d'))))
    >>> head1.value
    'a'
    >>> head1.next_node
    HashNode('b', HashNode('c', HashNode('d')))

    Nodes are unequal if the SLLs they head are structurally unequal:

    >>> HashNode('a', HashNode('b', HashNode('Q', HashNode('d')))) == head1
    False

    Heads of structurally equal SLLs are not merely equal, but the same object:

    >>> HashNode('a', HashNode('b', HashNode('c', HashNode('d')))) is head1
    True

    Equal values are treated as interchangeable, even across types:

    >>> HashNode(1.0) is HashNode(1) is HashNode(True)
    True
    >>> head3 = HashNode(0)
    >>> HashNode(False)
    HashNode(0)

    Like standard library containers, to handle NaNs, a node is always equal to
    itself even if its value isn't. Such values do NOT create duplicate nodes:

    >>> import math
    >>> HashNode(math.nan) is HashNode(math.nan) == HashNode(math.nan)
    True

    To build an SLL from an iterable of values, use from_iterable. This is a
    named constructor, not a top-level function. That is so it is always clear,
    at the call site, what class is being instantiated. But from_iterable uses
    no part of the HashNode interface, other than calling the class. It
    especially doesn't use or depend on any implementation details of HashNode.

    >>> HashNode.from_iterable(iter('abcd')) is head1
    True
    >>> head2 = HashNode.from_iterable(range(9000))
    >>> list(traverse(head2)) == list(range(9000))
    True

    The HashNode class keeps track of its instances in such a way that, once
    unreachable from the outside, they are immediately eligible for garbage
    collection. (test_sll.py and test_sll.txt have tests for this.)
    """

    __slots__ = ('_box', '_next_node', '__weakref__')

    _lock = threading.RLock()
    _already_locked = False
    _table = weakref.WeakValueDictionary()  # (value, next_node) -> node

    @classmethod
    def count_instances(cls):
        """Return the number of currently existing instances."""
        return len(cls._table)

    @classmethod
    def from_iterable(cls, values):
        """Make a singly linked list of the given values. Return the head."""
        try:
            backwards = reversed(values)
        except TypeError:
            backwards = reversed(list(values))

        acc = None
        for value in backwards:
            acc = cls(value, acc)
        return acc

    def __new__(cls, value, next_node=None):
        """Make a node or retrieve the suitable one that already exists."""
        # Since we are doing hash consing, the effects of allowing a next_node
        # of the wrong type are dire: the wrong behavior is both unintuitive
        # and global. So it is important to check the type of next_node, even
        # if runtime type-checking is not otherwise called for.
        if not isinstance(next_node, cls | None):
            raise TypeError(f'next_node must be a {cls.__name__} or None, not '
                            + type(next_node).__name__)

        # The key for a node accesses the node's element and successor through
        # weak references. This is important because the WeakValueTable holds
        # strong references to its keys. If an element has a strong reference
        # cycle back to the node that contains it, the cyclic garbage collector
        # will be able to clean it up when it is only accessible through the
        # table, but only if the table doesn't strongly refer into the cycle.
        box = _Box(value)
        key = (weakref.ref(box), next_node and weakref.ref(next_node))

        with cls._lock:
            if cls._already_locked:
                name = f'{cls.__name__}.__new__'
                message = f'{name} reentered through __hash__ or __eq__'
                raise RuntimeError(message)

            cls._already_locked = True
            try:
                return cls._table[key]
            except KeyError:
                node = super().__new__(cls)
                node._box = box
                node._next_node = next_node
                cls._table[key] = node
                return node
            finally:
                cls._already_locked = False

    def __repr__(self):
        """
        Code representation of this node. Shows the whole list.

        For simplicity, this is implemented in a straightforward recursive way,
        even though that means it raises RecursionError when called on the head
        node of a long singly linked list.
        """
        if self.next_node:
            return f'{type(self).__name__}({self.value!r}, {self.next_node!r})'
        return f'{type(self).__name__}({self.value!r})'

    @property
    def value(self):
        """The value held by this node."""
        return self._box.value

    @property
    def next_node(self):
        """The next node (the head of the tail of this node)."""
        return self._next_node

    @classmethod
    def draw(cls):
        """Draw the structure of all instances of HashNode."""
        # Nodes that are not strongly referenced may be collected, and thereby
        # removed from the table, at any time. WeakValueDictionary is in charge
        # of ensuring that no state gets corrupted as a result of this, and for
        # allowing iteration even though items may disappear at any time due to
        # that effect. But it is still not safe to modify the contents of the
        # WeakValueDictionary by any other mechanism during iteration. Further,
        # since weak-referenced objects may disappear at any time and their ids
        # reused, but we're using ids as node names to build the graph drawing,
        # we need a consistent snapshot of all nodes.
        #
        # Therefore, we materialize the table's values, synchronizing this with
        # the lock used by __new__. Nodes may be collected while this happens.
        # But materialization makes strong references, and next_node attributes
        # already hold strong references. So once materialization gets a node,
        # it and all nodes reachable from it are protected. So we will see all
        # nodes that appear in any SLL after any node we have seen. Having
        # thereby taken strong references to a consistent set of nodes, we can
        # be confident the graph we draw makes sense, and that we don't cause
        # any invariants to be violated. (Contrast recursion.leaf_sum_dec.)
        with cls._lock:
            nodes = list(cls._table.values())

        graph = graphviz.Digraph()

        # Add the null sentinel (the None object) to the graph.
        graph.node(str(id(None)), shape='point')

        # Add all actual singly linked list nodes to the graph.
        for node in nodes:
            graph.node(str(id(node)), label=html.escape(repr(node.value)))

        # Add the links (edges) between singly linked list nodes to the graph.
        for node in nodes:
            graph.edge(str(id(node)), str(id(node.next_node)))

        return graph


def traverse(head):
    """
    Lazily traverse a linked list. Yield values front to back.

    >>> short = HashNode(1, HashNode(5, HashNode(2, HashNode(4, HashNode(3)))))
    >>> list(traverse(short))
    [1, 5, 2, 4, 3]

    >>> long = HashNode.from_iterable(range(9000))
    >>> list(traverse(long)) == list(range(9000))
    True
    """
    while head:
        yield head.value
        head = head.next_node


if __name__ == '__main__':
    import doctest
    doctest.testmod()
