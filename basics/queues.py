"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of the types in this module do not override __repr__.
Eventually, however, that should be fixed (and this paragraph removed).
"""


class Queue:
    """Abstract class representing a generalized queue."""


class FifoQueue:
    """Abstract class representing a first-in first-out queue (a "queue")."""


class LifoQueue:
    """Abstract class representing a last-in first-out queue (a stack)."""


class DequeFifoQueue:
    """A FIFO queue (i.e., a "queue") based on a collections.deque."""


class AltDequeFifoQueue:
    """
    A FIFO queue (i.e., a "queue") based on a collections.deque.

    Like DequeFifoQueue but elements move through in the other direction.
    """


class SlowFifoQueue:
    """A FIFO queue (i.e., a "queue") based on a list. Quadratic dequeueing."""


class BiStackFifoQueue:
    """A FIFO queue (i.e., a "queue") based on two lists used as stacks."""


class ListLifoQueue:
    """A LIFO queue (i.e., a stack) based on a list."""


class DequeLifoQueue:
    """A LIFO queue (i.e., a stack) based on a collections.deque."""


class AltDequeLifoQueue:
    """
    A LIFO queue (i.e., a stack) based on a collections.deque.

    Like DequeLifoQueue but elements are pushed and popped at the other end.
    """
