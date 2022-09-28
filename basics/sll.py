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
object) represents the empty sublist. Viewed as part of this tree, nodes'
"next" pointers are parent pointers. Calling Node.draw() illustrates this by
building a graphviz.Digraph of the entire tree.

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
is public, and the absence of a node is represented by the None object.
"""

__all__ = ['Node']

import html
import threading
import weakref

import graphviz


class Node:
    """
    Immutable singly linked list node, using hash consing.

    See the sll module docstring for an explanation of the concepts involved.

    Inheriting from this class is not recommended.

    >>> head = Node('a', Node('b', Node('c', Node('d'))))
    >>> head
    Node('a', Node('b', Node('c', Node('d'))))
    >>> Node('a', Node('b', Node('c', Node('d')))) is head
    True
    >>> head2 = Node('x', Node('b', Node('c', Node('d'))))
    >>> head3 = Node('y', Node('b', Node('c', Node('d'))))
    >>> len({head, head2, head3})
    3
    >>> head.next_node is head2.next_node is head3.next_node
    True
    >>> hasattr(head, '__dict__')
    False
    """

    __slots__ = ('__weakref__', '_value', '_next_node')

    _lock = threading.Lock()
    _table = weakref.WeakValueDictionary()  # (value, next_node) -> node

    @classmethod
    def draw(cls):
        """Draw the structure of all instances of Node."""
        # Nodes that are not strongly referenced may be collected, and thereby
        # removed from the table, at any time. WeakValueDictionary is in charge
        # of ensuring that no state are corrupted as a result of this, and for
        # allowing iteration even though items may disappear at any time due to
        # that effect. But it is still not safe to modify the contents of the
        # WeakValueDictionary by any other mechanism during iteration. Further,
        # since weak-referenced objects may disappear at any time and their ids
        # reused, but we're using ids as node names to build the graph drawing,
        # we need a consistent snapshot of all nodes. Therefore, we materialize
        # the table's values, synchronizing this with the lock used by __new__.
        # Having taken strong references to a consistent set of nodes, we can
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
