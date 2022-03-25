"""Queues, in the general sense."""

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
    def enqueue(self):
        """Insert an element into this queue."""

    @abstractmethod
    def dequeue(self):
        """Extract an element from this queue."""


class FifoQueue(Queue):  # FIXME: For now, keep only the hierarchy rooted here.
    """Abstract class representing a first-in first-out queue (a "queue")."""

    __slots__ = ()

    # TODO: Add a create() method that opaquely instantiates some subclass.

    @abstractmethod
    def enqueue(self, item):
        """Insert an element at the "front" of this FIFO queue."""

    @abstractmethod
    def dequeue(self):
        """Extract the least recently inserted element from this FIFO queue."""


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    __slots__ = ()

    # TODO: Add a create() method that opaquely instantiates some subclass.

    @abstractmethod
    def enqueue(self, item):
        """Insert an item at the "top" of this LIFO queue."""

    @abstractmethod
    def dequeue(self, item):
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


class _ListOrDequeLifoQueue(LifoQueue):
    """ListLifoQueue/DequeLifoQueue base class (implementation detail)."""

    __slots__ = ('_items',)

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.pop()


class ListLifoQueue(_ListOrDequeLifoQueue):
    """A LIFO queue (i.e., a stack) based on a list."""

    __slots__ = ()

    def __init__(self):
        """Create a new list-based LIFO queue."""
        self._items = []


class DequeLifoQueue(_ListOrDequeLifoQueue):
    """A LIFO queue (i.e., a stack) based on a collections.deque."""

    __slots__ = ()

    def __init__(self):
        """Create a new deque-based LIFO queue."""
        self._items = collections.deque()
