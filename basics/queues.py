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
import bisect
import collections
import operator


class _Node:
    """Singly linked list node."""

    __slots__ = ('_element', 'next')

    def __init__(self, /, element, next_node=None):
        """Create a new node with the given element and optional next node."""
        self._element = element
        self.next = next_node

    def __repr__(self):
        """Eval-able representation of this linked list."""
        typename = type(self).__name__
        if self.next is None:
            return f'{typename}({self.element!r})'
        return f'{typename}({self.element!r}, {self.next!r})'

    @property
    def element(self):
        """The element held in this node."""
        return self._element


def _indexed_max(iterable):
    """Return the 0-based index to the maximum value, and that value."""
    try:
        return max(enumerate(iterable), key=operator.itemgetter(1))
    except ValueError as error:
        raise IndexError("can't find indexed maximum of zero items") from error


class Queue(ABC):
    """Abstract class representing a generalized queue."""

    __slots__ = ()

    @abstractmethod
    def __bool__(self):
        """Check if this queue has any elements."""
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        """The number of elements in this queue."""
        raise NotImplementedError()

    @abstractmethod
    def enqueue(self, item):
        """Put an item into this queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract and return an item from this queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Get the element that dequeue would return, with removing it."""
        raise NotImplementedError()


class FifoQueue(Queue):
    """Abstract class representing a first-in first-out queue (a "queue")."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Create an empty FIFO queue of this type or a reasonable subtype."""
        return (DequeFifoQueue if cls is FifoQueue else cls)()

    @abstractmethod
    def enqueue(self, item):
        """Insert an item at the back of this FIFO queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract the item from the front of this FIFO."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Return but don't remove the item at the front of this FIFO queue."""
        return NotImplementedError()


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Create an empty LIFO queue of this type or a reasonable subtype."""
        return (ListLifoQueue if cls is LifoQueue else cls)()

    @abstractmethod
    def enqueue(self, item):
        """Push an item to the top of this LIFO queue (stack)."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Pop and return an item from the top of this LIFO queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """Return but don't pop the item at the top of this LIFO queue."""
        raise NotImplementedError()


class PriorityQueue(Queue):
    """Abstract class representing a priority queue."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """
        Create an empty priority queue of this type or a reasonable subtype.
        """
        # FIXME: Default to BinaryMaxheap instead, once we have that class.
        return (FastEnqueueMaxPriorityQueue if cls is PriorityQueue else cls)()

    @abstractmethod
    def enqueue(self, item):
        """Insert an item into this priority queue."""
        raise NotImplementedError()

    @abstractmethod
    def dequeue(self):
        """Extract the maximum item from this priority queue."""
        raise NotImplementedError()

    @abstractmethod
    def peek(self):
        """
        Return but don't remove the maximum item from this priority queue.
        """
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
        """Create a new empty deque-based FIFO queue."""
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
        """Create a new empty deque-based FIFO queue."""
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
        """Create a new FIFO queue based on two stacks."""
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


class SinglyLinkedListFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a singly linked list."""

    __slots__ = ('_front', '_back', '_count')

    def __init__(self):
        """Create a new FIFO queue based on a singly linked list."""
        self._front = self._back = None
        self._count = 0

    def __bool__(self):
        return self._count != 0

    def __len__(self):
        return self._count

    def enqueue(self, item):
        if self:
            self._back.next = _Node(item)
            self._back = self._back.next
        else:
            self._front = self._back = _Node(item)

        self._count += 1

    def dequeue(self):
        item = self.peek()

        if self._count == 1:
            self._front = self._back = None
        else:
            self._front = self._front.next

        self._count -= 1

        return item

    def peek(self):
        if not self:
            raise LookupError('empty FIFO queue has no front element')

        return self._front.element


class ListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a list."""

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new LIFO queue based on a list."""
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
        """Create a new LIFO queue based on a deque."""
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
        """Create a new LIFO queue based on a deque (alternative approach)."""
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


class SinglyLinkedListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a singly linked list."""

    __slots__ = ('_head', '_count')

    def __init__(self):
        """Create a a new LIFO queue based on a singly linked list."""
        self._head = None
        self._count = 0

    def __bool__(self):
        return self._head is not None

    def __len__(self):
        return self._count

    def enqueue(self, item):
        self._head = _Node(item, self._head)
        self._count += 1

    def dequeue(self):
        item = self.peek()
        self._head = self._head.next
        self._count -= 1
        return item

    def peek(self):
        if not self:
            raise LookupError('empty LIFO queue has no top element')

        return self._head.element


class FastEnqueueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(1) enqueue, O(n) dequeue, and O(n) peek."""

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new max priority queue supporting fast insertion."""
        self._items = []

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        i, _ = _indexed_max(self._items)
        self._items[i], self._items[-1] = self._items[-1], self._items[i]
        return self._items.pop()

    def peek(self):
        _, item = _indexed_max(self._items)
        return item


class FastDequeueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(n) enqueue, O(1) dequeue, and O(1) peek."""

    __slots__ = ('_items',)

    def __init__(self):
        """Create a new max priority queue supporting fast extraction."""
        self._items = []

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def enqueue(self, item):
        bisect.insort_right(self._items, item)

    def dequeue(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1]
