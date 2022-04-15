"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of types in this module won't override __repr__. Eventually,
that should be fixed (and this note removed). Design decisions to accompany
implementing __repr__ may include: Should (all or some of) the queue types be
constructible from an iterable? Should they themselves be iterable? Reversible?
"""


class Queue:
    """Abstract class representing a generalized queue."""


class FifoQueue:
    """Abstract class representing a first-in first-out queue (a "queue")."""


class LifoQueue:
    """Abstract class representing a last-in first-out queue (a stack)."""


class PriorityQueue:
    """Abstract class representing a priority queue."""


class DequeFifoQueue:
    """A FIFO queue (i.e., a "queue") based on a collections.deque."""


class AltDequeFifoQueue:
    """
    A FIFO queue (i.e., a "queue") based on a collections.deque.

    Like DequeFifoQueue but elements move through in the other direction.
    """


class SlowFifoQueue:
    """A FIFO queue (i.e., a "queue") based on a list. Linear-time dequeue."""


class BiStackFifoQueue:
    """A FIFO queue (i.e., a "queue") based on two lists used as stacks."""


class SinglyLinkedListFifoQueue:
    """A FIFO queue (i.e., a "queue") based on a singly linked list."""


class ListLifoQueue:
    """A LIFO queue (i.e., a stack) based on a list."""


class DequeLifoQueue:
    """A LIFO queue (i.e., a stack) based on a collections.deque."""


class AltDequeLifoQueue:
    """
    A LIFO queue (i.e., a stack) based on a collections.deque.

    Like DequeLifoQueue but elements are pushed and popped at the other end.
    """


class SinglyLinkedListLifoQueue:
    """A LIFO queue (i.e., a stack) based on a singly linked list."""


class FastEnqueueMaxPriorityQueue:
    """A max priority queue with O(1) enqueue, O(n) dequeue, and O(n) peek."""


class FastDequeueMaxPriorityQueue:
    """A max priority queue with O(n) enqueue, O(1) dequeue, and O(1) peek."""
