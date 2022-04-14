"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of types in this module won't override __repr__. Eventually,
that should be fixed (and this note removed). Design decisions to accompany
implementing __repr__ may include: Should (all or some of) the queue types be
constructible from an iterable? Should they themselves be iterable? Reversible?
"""

from abc import ABC, abstractmethod
import bisect
import collections
import operator


def _identity_function(arg):
    """Identity function. Returns its argument unchanged."""
    return arg


def _indexed_min(iterable, *, key):
    """
    Find the minimum of enumerate(iterable), comparing by value (not index).

    If iterable is empty, IndexError is raised. This differs from min, which
    raises ValueError when passed an empty iterable.
    """
    try:
        return min(enumerate(iterable), key=operator.itemgetter(1))
    except ValueError as error:
        raise IndexError("can't get indexed min of empty iterable") from error


# TODO: Extract something like this class to compare.py, for reuse.
class _ReverseComparing:
    """Opaque wrapper, providing reversed order comparisons."""

    __slots__ = ('_item',)

    def __init__(self, item, *, key=None):
        """
        Create a reverse-comparing wrapper for an item.

        A key preselector function may be passed as key.
        """
        self._item = (item if key is None else key(item))

    def __eq__(self, other):
        if not isinstance(other, _ReverseComparing):
            return NotImplemented
        return other._item == self._item

    def __lt__(self, other):
        if not isinstance(other, _ReverseComparing):
            return NotImplemented
        return other._item < self._item

    def __gt__(self, other):
        if not isinstance(other, _ReverseComparing):
            return NotImplemented
        return other._item > self._item

    def __le__(self, other):
        if not isinstance(other, _ReverseComparing):
            return NotImplemented
        return other._item <= self._item

    def __ge__(self, other):
        if not isinstance(other, _ReverseComparing):
            return NotImplemented
        return other._item >= self._item

    def __hash__(self):
        return hash(self._item)


class Queue(ABC):
    """Abstract class representing a generalized queue."""

    __slots__ = ()

    @abstractmethod
    def __bool__(self):
        """True if this queue contains any elements, False if it is empty."""
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        """The number of elements in this queue."""
        raise NotImplementedError()

    @abstractmethod
    def enqueue(self, item):
        """Insert an element into this queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract an element from this queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Get the element that dequeue would extract and return."""
        raise NotImplementedError()


class FifoQueue(Queue):
    """Abstract class representing a first-in first-out queue (a "queue")."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Opaquely instantiate some reasonable concrete FifoQueue subclass."""
        return (DequeFifoQueue if cls is FifoQueue else cls)()

    @abstractmethod
    def enqueue(self, item):
        """Insert an element at the "front" of this FIFO queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract the least recently inserted element from this FIFO queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Return the least recently inserted element from this FIFO queue."""
        raise NotImplementedError()


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Opaquely instantiate some reasonable concrete LifoQueue subclass."""
        return (ListLifoQueue if cls is LifoQueue else cls)()

    @abstractmethod
    def enqueue(self, item):
        """Insert an item at the "top" of this LIFO queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract the most recently inserted element from this LIFO queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Return the most recently inserted element from this LIFO queue."""
        raise NotImplementedError()


class PriorityQueue(Queue):
    """Abstract class representing a priority queue."""

    __slots__  = ()

    @classmethod
    def create(cls):
        """Opaquely instantiate some reasonable PriorityQueue subclass."""
        # TODO: Once BinaryMinheapPriorityQueue is implemented, default to it.
        return (FastEnqueuePriorityQueue if cls is PriorityQueue else cls)()

    @abstractmethod
    def enqueue(self, item):
        """Insert an item into this priority queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract the priority element from this priority queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Return (but keep) the priority element from this priority queue."""
        raise NotImplementedError()


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

    def peek(self):
        return self._items[0]


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

    def peek(self):
        return self._items[-1]


class SlowFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a list. Linear-time dequeue."""

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

    def peek(self):
        return self._items[0]


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

    def peek(self):
        return self._out[-1] if self._out else self._in[0]


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

    def peek(self):
        return self._items[-1]


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

    def peek(self):
        return self._items[-1]


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

    def peek(self):
        return self._items[0]


class _FlatPriorityQueueBase(PriorityQueue):
    """Implementation detail for code reuse implementing priority queues."""

    __slots__ = ('_key', '_items')

    def __init__(self, *, key=None, reverse=False):
        """Create a new empty priority queue."""
        if reverse:
            self._key = lambda item: _ReverseComparing(item, key=key)
        elif key is None:
            self._key = _identity_function
        else:
            self._key = key

        self._items = []

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)


class FastEnqueuePriorityQueue(_FlatPriorityQueueBase):
    """A priority queue with O(1) enqueue, O(n) dequeue, and O(n) peek."""

    __slots__ = ()

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        i, _ = _indexed_min(self._items, key=self._key)
        self._items[i], self._items[-1] = self._items[-1], self._items[i]
        return self._items.pop()

    def peek(self):
        _, value = _indexed_min(self._items, key=self._key)
        return value

    def _indexed_priority_item(self):
        return _indexed_min(self._items, key=self._key)


class FastDequeuePriorityQueue(_FlatPriorityQueueBase):
    """A priority queue with O(n) enqueue, O(1) dequeue, and O(1) peek."""

    __slots__ = ()

    def __init__(self, *, key=None, reverse=False):
        super().__init__(key=key, reverse=not reverse)

    def enqueue(self, item):
        bisect.insort(self._items, item, key=self._key)

    def dequeue(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1]
