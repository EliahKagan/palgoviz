#!/usr/bin/env python

"""
Immutable singly linked lists using hash consing to share tails globally.

Hash consing is an advanced technique. This project currently has no module for
presenting singly linked lists in an introductory fashion. But a basic use of
singly linked lists, with no specialized techniques, appears in queues.py,
which contains an SLL-based FIFO queue and an SLL-based LIFO queue.

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
then it is guaranteed that those two variables refer to the same node object.
Therefore, for sll.Node objects, reference-based equality comparison is also
structural equality comparison (for the lists they are the head nodes of). This
is one of the benefits of hash consing.

Nonetheless, in practice it may still be useful for the node class to be a
private implementation detail, and for each singly linked list taken as a whole
to be represented by an instance of another class that implements the sequence
protocol (providing __len__, __iter__, and other methods; see the documentation
on collections.abc.Sequence). Alternatively, the empty singly linked list could
be represented by a special-purpose singleton rather than None, where both the
Node class and that singleton class implement the sequence protocol. For
conceptual clarity and simplicity of presentation, we do neither here. Our Node
class is public, and the absence of a node is represented by the None object.
"""

# TODO: Decide if we want a module giving an introductory treatment of singly
# linked lists. If so, consider having the sll module's top-level content be
# that, and moving what's currently here to a submodule called hashed. Either
# way, we should document the situation in the module docstring, so it is clear
# whether major breaking changes to the structure of sll are planned.

__all__ = ['Node', 'traverse']

import abc
import html
import threading
import weakref

import graphviz


class _NodeBase:
    """Base class for sharing Node and TypedNode implementation details."""
    # FIXME: Needs implementation. Move most Node code into here.


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
    >>> Node('a', object())  # Validated, to avoid corrupting global state.
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


class TypedNode:
    """
    Immutable singly linked list node. Like Node but type-sensitive.

    Like Node, TypedNode uses thread-safe global guaranteed hash consing,
    TypedNode instances are equal only if they are the same object, and
    inheriting from TypedNode is not recommended. But TypedNode's equality
    comparison is more discerning: nodes compare equal when all corresponding
    values in the SLLs they head are not just equal but also of the same types.

    This behavior is strange, because it means TypedNode SLLs constructed from
    equal Python lists need not be equal. Node is preferable unless you have a
    specific need for TypedNode. There is a third way that seems better until
    considered carefully: allow heads of SLLs that can only be distinguished by
    element types to be separate objects that compare equal. That has two
    problems: First, equality comparison on nodes would no longer be reference
    equality and would no longer take O(1) time in the worst case. Second, the
    original problem would come back if nested SLLs are used, because heads of
    SLLs whose corresponding elements can only be distinguished by type would,
    while nonidentical, be equal and of the same type (the node type).

    Besides doctests, Node and TypedNode are implemented with almost zero code
    duplication. Neither inherits from the other, and either would continue to
    work if the other were removed. They also behave independently at runtime.
    """
    # FIXME: Needs implementation.


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
