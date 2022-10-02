#!/usr/bin/env python

# NOTE: If you find this code by searching for hash consing in Python, it will
# likely NOT meet your needs, because it can leak heterogeneous cycles through
# the data structure that tracks existing nodes. (See details below.)

"""
Immutable singly linked lists using hash consing to share tails globally.

Hash consing is an advanced technique. This project currently has no module for
presenting singly linked lists in an introductory fashion. But a basic use of
singly linked lists, with no specialized techniques, appears in queues.py,
which contains an SLL-based FIFO queue and an SLL-based LIFO queue.

NOTE: Before using this module or the techniques it presents, please make sure
to read "The problem of heterogeneous cycles" below. If you have an application
that requires hash consing, it is likely this code will NOT do what you need!


### Hash consing

With hash consing (when global and guaranteed, as here), all singly linked
lists that use the hash-consed node type, and that exist in memory at the same
time, make up a single "upside-down" tree. The tree's root (here, the None
object) represents the empty sublist. Viewed as part of this tree, next_node
pointers are parent pointers. Calling Node.draw() illustrates this by building
a graphviz.Digraph of the entire tree.

The Node type in this module uses reference-based equality comparison, but
singly linked lists that use this Node type always share the longest suffix
possible, including when that is the whole linked list. So if two variables
refer to the head nodes of lists with equal values appearing in the same order,
then it is guaranteed that those two variables refer to the same node object
(assuming there are no bugs!). Therefore, for sll.Node objects, reference-based
equality comparison is also structural equality comparison (for the lists they
are the head nodes of). This is one of the benefits of hash consing.

Hash consing is applicable to any immutable node-based data structure whose
nodes make up a directed acyclic graph. This includes, but is not limited to,
binary and n-ary trees without parent pointers. This is analogous to the case
of singly linked lists. (A binary tree node has two child pointers, while a
singly linked list node has one child pointer.) Only SLLs are implemented here.


### The problem of heterogeneous cycles

This hash consing implementation can leak heterogeneous cycles and is thus
unsuitable for general use. Two skipped tests in test_sll.py related to this:

  - TestNode.test_single_simple_heterogeneous_cycle_does_not_leak
  - TestNode.test_nontrivial_heterogeneous_cycles_do_not_leak

In a homogeneous cycle, following nodes' next_node (successor) and/or value
(element) attributes would bring one back to an ancestor node. Since nodes are
immutable, and their elements are required to be immutable, homogeneous cycles
do not occur without code that uses this module having a severe design bug,
such a mutable hashable type (that is used as an element type), or violating
encapsulation. Nodes may be shared by many linked lists. Nodes may also be
nested: being themselves immutable and hashable, nodes may appear as elements
of other nodes. None of this prevents objects from being garbage collected.

Heterogeneous cycles are another story. An object can be immutable in the sense
that its value never changes, yet still hold mutable state that doesn't affect
its value. It's reasonable for such an object to be hashable. Most classes work
this way, inheriting __eq__ and __hash__ from object but allowing arbitrary
attributes in their instance dictionaries. So we wouldn't want to prohibit most
such as objects as elements. But what if a node's element, after being stored
in the node, gains an attribute that doesn't participate in equality comparison
or hashing but refers, directly or indirectly, back to the node itself?

That is a heterogenous cycle: part of the cycle is through an object of an
unrelated type. Our private table that looks up nodes by their elements and
successors holds weak references to the nodes it returns, so it doesn't prevent
them from being garbage collected. But the elements and successors are held by
strong references. That's normally no problem: as long as a node exists, it
keeps its element and successor alive anyway, and when a node is destroyed, the
table takes care of removing the entry for it (using weakref callbacks). But if
there is a chain of strong references from the element back to the node, then
the table holds a strong reference to the element, which holds a strong
reference to the node, so the node is reachable and can't be collected. Unless
the heterogeneous cycle is somehow broken, the entry is never removed from the
table, since it would only be removed when the node it keeps reachable becomes
unreachable and is collected, which its presence ensures cannot happen.

In many uses, client code can ensure no heterogeneous cycle forms. But without
knowing the use case, this can't be ensured. So it would be good if the node
type could prevent or break such cycles. Since a node's element and successor
always exist as long as the node does, it seems the table could hold weak
instead of strong references to them. But this only works if the callback the
table registers to remove the entry removes it without looking up the entry by
element and successor, since the element would no longer exist to be compared
for equality to other elements in the table. The weakref.WeakValueTable class
doesn't promise not to do that, and the CPython implementation, which stores
its entries in an underlying dict instance in order satisfy its atomicity
guarantees, does it. (Not all objects in Python are weak-referenceable, but if
that were the only problem, it could be solved by having both the table and
node refer to to a weak-referenceable wrapper object standing in front of the
element: the table, so the element is not strongly reachable, and the node, to
ensure the element is not collected too early.)

So the problem of heterogeneous cycles in hash consing seems tricky to solve in
Python. Beyond verifying the above concrete claims, efforts to solve it have
not been undertaken in this project, as of this writing. This module is thus
limited. Note that this should probably not be considered a problem with hash
consing itself: production quality hash consing implementations often don't
have to deal with this at all, because they are often for languages where
objects never hold mutable state that doesn't contribute to their values and/or
are implemented together with, and sometimes part of, the garbage collector.
"""

# FIXME: Put this in a submodule of sll. Probably called it "hashed". Do this
# even if there is currently no other code to go in the sll module, so this is
# not mistaken for being an acceptable way to teach singly linked lists (this
# is about __new__ and weak references, not about introducing SLLs). This may
# also help make clear that the code here is not suitable for most use cases,
# even when global guaranteed hash consing is desired.

__all__ = ['Node', 'traverse']

import html
import threading
import weakref

import graphviz


class Node:
    """
    Immutable singly linked list node, using hash consing. Thread-safe.

    See the sll module docstring for information on the concepts involved. Node
    equality implies identity. Inheriting from this class is not recommended.

    >>> head1 = Node('a', Node('b', Node('c', Node('d'))))
    >>> head1
    Node('a', Node('b', Node('c', Node('d'))))
    >>> head1.value
    'a'
    >>> head1.next_node
    Node('b', Node('c', Node('d')))

    >>> Node('a', Node('b', Node('c', Node('d')))) is head1
    True
    >>> head2 = Node('x', Node('b', Node('c', Node('d'))))
    >>> len({head1, head2}), len({head1.next_node, head2.next_node})
    (2, 1)
    >>> head1.next_node is head2.next_node
    True
    >>> Node('a', Node('b', Node('c'))) is head1
    False
    >>> hasattr(head1, '__dict__')  # Nodes should have a low memory footprint.
    False
    >>> Node('a', object())  # Validated, to protect shared state.
    Traceback (most recent call last):
      ...
    TypeError: next_node must be a Node or None, not object

    Equal values are treated as interchangeable even across types (which is a
    reasonable design choice, but we may add a separate TypedNode class later):

    >>> Node(1.0) is Node(1) is Node(True)
    True
    >>> head3 = Node(0)
    >>> Node(False)
    Node(0)

    To build an SLL from an iterable of values, use from_iterable. This is a
    named constructor instead of a top-level function, so it's clear, at the
    call site, what type is being instantiated. But its implementation uses no
    part of the Node interface, other than calling the class. It especially
    does not use or depend on any implementation details of Node.

    >>> Node.from_iterable([]) is None
    True
    >>> Node.from_iterable('abcd') is Node.from_iterable(iter('abcd')) is head1
    True
    >>> head4 = Node.from_iterable(range(9000))
    >>> list(traverse(head4)) == list(range(9000))
    True

    These tests assume no other code in the process running the doctests has
    created and *kept* references to Node instances:

    >>> from testing import collect_if_not_ref_counting as coll
    >>> coll(); Node.count_instances()
    9006
    >>> head5 = Node.from_iterable(range(-100, 9000)); Node.count_instances()
    9106
    >>> del head4, head5; coll(); Node.count_instances()
    6
    >>> head3 = head1; coll(); Node.count_instances()
    5
    >>> del head1, head3; coll(); Node.count_instances()
    4
    >>> del head2; coll(); Node.count_instances()
    0
    """

    __slots__ = ('__weakref__', '_value', '_next_node')

    _lock = threading.Lock()
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

        with cls._lock:
            try:
                return cls._table[value, next_node]
            except KeyError:
                node = super().__new__(cls)
                node._value = value
                node._next_node = next_node
                cls._table[value, next_node] = node
                return node

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
        return self._value

    @property
    def next_node(self):
        """The next node (the head of the tail of this node)."""
        return self._next_node

    @classmethod
    def draw(cls):
        """Draw the structure of all instances of Node."""
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

    >>> it = traverse(None)
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(traverse(Node(1, Node(5, Node(2, Node(4, Node(3)))))))
    [1, 5, 2, 4, 3]

    >>> from itertools import islice
    >>> from types import SimpleNamespace as SN
    >>> head = SN(value=7, next_node=SN(value=8, next_node=SN(value=9)))
    >>> head.next_node.next_node.next_node = head  # Make a simple cycle.
    >>> list(islice(traverse(head), 24))  # Test laziness.
    [7, 8, 9, 7, 8, 9, 7, 8, 9, 7, 8, 9, 7, 8, 9, 7, 8, 9, 7, 8, 9, 7, 8, 9]

    >>> list(traverse(Node.from_iterable(range(9000)))) == list(range(9000))
    True
    """
    while head:
        yield head.value
        head = head.next_node


if __name__ == '__main__':
    import doctest
    doctest.testmod()
