"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of these queue types might not override __repr__. Eventually,
that should be fixed (and this note removed). Design decisions to accompany
implementing __repr__ might include: Should (all or some of) the queue types
support construction from an iterable? Be iterable themselves? Reversible?
Should distinct queue objects ever be equal? To objects of a different type?
"""

from abc import ABC, abstractmethod
import collections


class Queue(ABC):
    """Abstract class representing a generalized queue."""

    @abstractmethod
    def __bool__(self):
        ...

    @abstractmethod
    def __len__(self):
        ...

    @abstractmethod
    def enqueue(self, item):
        ...

    @abstractmethod
    def dequeue(self):
        ...

    @abstractmethod
    def peek(self):
        ...


class FifoQueue(Queue):
    """Abstract class representing a first-in first-out queue (a "queue")."""

    @classmethod
    def create(cls):
        """Creates a FifoQueue instance."""
        if cls is FifoQueue:
            return DequeFifoQueue()
        return cls()


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    @classmethod
    def create(cls):
        """Creates a LifoQueue instance."""
        if cls is LifoQueue:
            return ListLifoQueue()
        return cls()


class PriorityQueue(Queue):
    """Abstract class representing a priority queue."""

    # TODO: Investigate which PriorityQueue should be default.
    @classmethod
    def create(cls):
        """Creates a LifoQueue instance."""
        if cls is PriorityQueue:
            return FastEnqueueMaxPriorityQueue()
        return cls()


class DequeFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a collections.deque."""

    __slots__ = ('_queue',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._queue = collections.deque()

    def __bool__(self):
        return bool(self._queue)

    def __len__(self):
        return len(self._queue)

    def enqueue(self, item):
        self._queue.append(item)

    def dequeue(self):
        return self._queue.popleft()

    def peek(self):
        return self._queue[0]


class AltDequeFifoQueue(FifoQueue):
    """
    A FIFO queue (i.e., a "queue") based on a collections.deque.

    Like DequeFifoQueue but elements move through in the other direction.
    """

    __slots__ = ('_queue',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._queue = collections.deque()

    def __bool__(self):
        return bool(self._queue)

    def __len__(self):
        return len(self._queue)

    def enqueue(self, item):
        self._queue.appendleft(item)

    def dequeue(self):
        return self._queue.pop()

    def peek(self):
        return self._queue[-1]


class SlowFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a list. Linear-time dequeue."""

    __slots__ = ('_list',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._list = []

    def __bool__(self):
        return bool(self._list)

    def __len__(self):
        return len(self._list)

    def enqueue(self, item):
        self._list.append(item)

    def dequeue(self):
        return self._list.pop(0)

    def peek(self):
        return self._list[0]


class BiStackFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on two lists used as stacks."""


class SinglyLinkedListFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a singly linked list."""


class ListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a list."""

    __slots__ = ('_list',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._list = []

    def __bool__(self):
        return bool(self._list)

    def __len__(self):
        return len(self._list)

    def enqueue(self, item):
        self._list.append(item)

    def dequeue(self):
        return self._list.pop()

    def peek(self):
        return self._list[-1]


class DequeLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a collections.deque."""

    __slots__ = ('_queue',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._queue = collections.deque()

    def __bool__(self):
        return bool(self._queue)

    def __len__(self):
        return len(self._queue)

    def enqueue(self, item):
        self._queue.append(item)

    def dequeue(self):
        return self._queue.pop()

    def peek(self):
        return self._queue[-1]


class AltDequeLifoQueue(LifoQueue):
    """
    A LIFO queue (i.e., a stack) based on a collections.deque.

    Like DequeLifoQueue but elements are pushed and popped at the other end.
    """

    __slots__ = ('_queue',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._queue = collections.deque()

    def __bool__(self):
        return bool(self._queue)

    def __len__(self):
        return len(self._queue)

    def enqueue(self, item):
        self._queue.appendleft(item)

    def dequeue(self):
        return self._queue.popleft()

    def peek(self):
        return self._queue[-0]


class SinglyLinkedListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a singly linked list."""


class FastEnqueueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(1) enqueue, O(n) dequeue, and O(n) peek."""

    __slots__ = ('_list',)

    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._list = []

    def __bool__(self):
        return bool(self._list)

    def __len__(self):
        return len(self._list)

    def enqueue(self, item):
        if self._list and item < self._list[-1]:
            self._list.insert(-1, item)
        else:
            self._list.append(item)

    def dequeue(self):
        return self._list.pop()

    def peek(self):
        return self._list[-1]


class FastDequeueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(n) enqueue, O(1) dequeue, and O(1) peek."""
