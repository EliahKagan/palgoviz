#!/usr/bin/env python

"""
Immutable singly linked lists using hash consing to share tails globally.

Hash consing is an advanced technique. This project currently has no module
dedicated to presenting singly linked lists in an introductory fashion. But a
basic use of singly linked lists, with no specialized techniques, appears in
queues.py, which contains an SLL-based FIFO queue and an SLL-based LIFO queue.

With hash consing--when global and guaranteed, as here--all SLLs that use the
hash-consed node type, existing in memory at any given time, form a single
"upside-down" tree. Its root (here, None) represents the empty sublist. Viewed
as part of this tree, next_node pointers are parent pointers. HashNode.draw()
illustrates this by building a graphviz.Digraph of the whole tree.

The HashNode type in this module uses reference-based equality comparison. But
HashNode-based SLLs always share the longest suffix possible, including when
that suffix is the whole SLL. So if two variables refer to heads of SLLs whose
values are equal and in the same order, those variables are guaranteed to refer
to the same node object. That is, for HashNode objects, reference equality is
the same as structural equality (of the linked lists they head). This is one of
the benefits of hash consing.

Hash consing can be applied to any immutable node-based data structure whose
nodes make up a directed acyclic graph. This includes, but is not limited to,
binary and n-ary trees without parent pointers. This is analogous to the case
of singly linked lists. (A binary tree node has two child pointers; a singly
linked list node has one "child" pointer.) Only SLLs are implemented here.
"""

__all__ = ['HashNode', 'traverse']


class HashNode:
    """
    Immutable singly linked list node, using hash consing. Thread-safe.

    See the sll module docstring regarding the concepts involved. HashNode
    equality implies identity. Inheriting from this class is not recommended.

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

    The uniqueness guarantee--that node equality implies identity--relies on
    each object ever used as an element being immutable, in the sense that its
    value never changes. Objects mutable (in that sense) shouldn't be hashable,
    so this restriction can only lead to problems in the presence of severe
    bugs in code outside this module: use of a hashable mutable type, or an
    encapsulation violation mutating an object considered immutable.

    Calling HashNode with a non-hashable element fails, but it is guaranteed to
    be safe. No HashNode is created, and shared state is not corrupted.

    >>> HashNode([])
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'list'

    However, HashNode uniqueness is not guaranteed if nodes may be resurrected.
    Weak reference callbacks are ideally called after the referent is already
    collected--after even other objects' __del__ methods that could resurrect
    it have run. But this is not guaranteed. Resurrecting a node after its
    weakref callbacks are called will preserve it after HashNode forgets about
    it. A duplicate node could then be created (and will compare unequal). The
    usual practice of rarely writing __del__ methods and, when one really must,
    trying hard to avoid resurrecting anything, should avoid this in practice.

    To build an SLL from an iterable of values, use from_iterable. This is a
    named constructor, not a top-level function. That is so it is always clear,
    looking at the call site, what class is being instantiated. But
    from_iterable uses no part of the HashNode interface, other than calling
    the class. It especially doesn't use or depend on any implementation
    details of HashNode.

    >>> HashNode.from_iterable(iter('abcd')) is head1
    True
    >>> head2 = HashNode.from_iterable(range(9000))
    >>> list(traverse(head2)) == list(range(9000))
    True

    The HashNode class keeps track of its instances in such a way that, once
    unreachable from the outside, they are immediately eligible for garbage
    collection. (test_sll.py and test_sll.txt have tests for this.)
    """
    # FIXME: Implement this.


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
