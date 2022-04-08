"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of the types in this module do not override __repr__.
Eventually, however, that should be fixed (and this paragraph removed).
"""

from abc import ABC, abstractmethod
import collections


class Queue(ABC):
    """Abstract class representing a generalized queue."""

    __slots__ = ()

    @abstractmethod
    def __bool__(self):
        """True if this queue contains any elements, False if it is empty."""

    @abstractmethod
    def __len__(self):
        """The number of elements in this queue."""

    @abstractmethod
    def enqueue(self, item):
        """Insert an element into this queue."""

    @abstractmethod
    def dequeue(self):
        """Extract an element from this queue."""


class FifoQueue(Queue):
    """Abstract class representing a first-in first-out queue (a "queue")."""

    __slots__ = ()

    @staticmethod
    def create():
        """Opaquely instantiate some reasonable concrete FifoQueue subclass."""
        return DequeFifoQueue()

    @abstractmethod
    def enqueue(self, item):
        """Insert an element at the "front" of this FIFO queue."""

    @abstractmethod
    def dequeue(self):
        """Extract the least recently inserted element from this FIFO queue."""


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    __slots__ = ()

    @staticmethod
    def create():
        """Opaquely instantiate some reasonable concrete LifoQueue subclass."""
        return ListLifoQueue()

    @abstractmethod
    def enqueue(self, item):
        """Insert an item at the "top" of this LIFO queue."""

    @abstractmethod
    def dequeue(self):
        """Extract the most recently inserted element from this LIFO queue."""


class DequeFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a collections.deque."""

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new empty deque-based FIFO queue."""
        self._items = collections.deque()

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.popleft()


class AltDequeFifoQueue(FifoQueue):
    """
    A FIFO queue (i.e., a "queue") based on a collections.deque.

    Like DequeFifoQueue but elements move through in the other direction.
    """

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new empty alternative deque-based FIFO queue."""
        self._items = collections.deque()

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.appendleft(item)

    def dequeue(self):
        return self._items.pop()


class SlowFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a list. Quadratic dequeueing."""

    __slots__ = ('_items',)

    def __init__(self):
        """"Create a new slow list-based FIFO queue."""
        self._items = []

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.pop(0)


class BiStackFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on two lists used as stacks."""

    __slots__ = ('_in', '_out')

    def __init__(self):
        """Create a new empty FIFO queue (based on two stacks)."""
        self._in = []
        self._out = []

    def __bool__(self):
        return bool(self._in or self._out)

    def __len__(self):
        return len(self._in) + len(self._out)

    def enqueue(self, item):
        self._in.append(item)

    def dequeue(self):
        if not self._out:
            while self._in:
                self._out.append(self._in.pop())

        return self._out.pop()


class ListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a list."""

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new list-based LIFO queue."""
        self._items = []

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.pop()


class DequeLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a collections.deque."""

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new empty deque-based LIFO queue."""
        self._items = collections.deque()

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.pop()


class AltDequeLifoQueue(LifoQueue):
    """
    A LIFO queue (i.e., a stack) based on a collections.deque.

    Like DequeLifoQueue but elements are pushed and popped at the other end.
    """

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new empty alternative deque-based LIFO queue."""
        self._items = collections.deque()

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.appendleft(item)

    def dequeue(self):
        return self._items.popleft()
