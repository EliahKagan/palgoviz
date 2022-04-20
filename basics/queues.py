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
    __slots__ = ()

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

    __slots__ = ()

    @classmethod
    def create(cls):
        """Creates a FifoQueue instance."""
        if cls is FifoQueue:
            return DequeFifoQueue()
        return cls()


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Creates a LifoQueue instance."""
        if cls is LifoQueue:
            return ListLifoQueue()
        return cls()


class PriorityQueue(Queue):
    """Abstract class representing a priority queue."""

    __slots__ = ()

    # TODO: Investigate which PriorityQueue should be default.
    @classmethod
    def create(cls):
        """Creates a LifoQueue instance."""
        if cls is PriorityQueue:
            return FastEnqueueMaxPriorityQueue()
        return cls()


class DequeFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a collections.deque."""

    __slots__ = ('_deque',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeFifoQueue from an empty deque."""
        self._deque = collections.deque()

    def __bool__(self):
        return bool(self._deque)

    def __len__(self):
        return len(self._deque)

    def enqueue(self, item):
        self._deque.append(item)

    def dequeue(self):
        return self._deque.popleft()

    def peek(self):
        return self._deque[0]


class AltDequeFifoQueue(FifoQueue):
    """
    A FIFO queue (i.e., a "queue") based on a collections.deque.

    Like DequeFifoQueue but elements move through in the other direction.
    """

    __slots__ = ('_deque',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct an AltDequeFifoQueu from an empty deque."""
        self._deque = collections.deque()

    def __bool__(self):
        return bool(self._deque)

    def __len__(self):
        return len(self._deque)

    def enqueue(self, item):
        self._deque.appendleft(item)

    def dequeue(self):
        return self._deque.pop()

    def peek(self):
        return self._deque[-1]


class SlowFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a list. Linear-time dequeue."""

    __slots__ = ('_list',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a SlowFifoQueue from an empty list."""
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

    __slots__ = ('_head','_tail', '_len')

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a SinglyLinkedListFifoQueue from an empty Sll."""
        self._head = None
        self._tail = None
        self._len = 0

    def __bool__(self):
        return bool(self._head)

    def __len__(self):
        return self._len

    def enqueue(self, item):
        new_node = _Node(item)
        if not self._head:
            new_node.nextn = self._head
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.nextn = new_node
            self._tail = new_node
        self._len += 1

    def dequeue(self):
        if self._head:
            result = self._head.value
            self._head = self._head.nextn
            if not self._head:
                self._tail = None
            self._len -= 1
            return result
        else:
            raise LookupError("Can't dequeue from empty queue")

    def peek(self):
        if self._head:
            return self._head.value
        else:
            raise LookupError("Can't peek from empty queue")


class ListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a list."""

    __slots__ = ('_list',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a ListLifoQueue from an empty list."""
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

    __slots__ = ('_deque',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a DequeLifoQueue from an empty deque."""
        self._deque = collections.deque()

    def __bool__(self):
        return bool(self._deque)

    def __len__(self):
        return len(self._deque)

    def enqueue(self, item):
        self._deque.append(item)

    def dequeue(self):
        return self._deque.pop()

    def peek(self):
        return self._deque[-1]


class AltDequeLifoQueue(LifoQueue):
    """
    A LIFO queue (i.e., a stack) based on a collections.deque.

    Like DequeLifoQueue but elements are pushed and popped at the other end.
    """

    __slots__ = ('_deque',)

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a AltDequeLifoQueue from an empty deque."""
        self._deque = collections.deque()

    def __bool__(self):
        return bool(self._deque)

    def __len__(self):
        return len(self._deque)

    def enqueue(self, item):
        self._deque.appendleft(item)

    def dequeue(self):
        return self._deque.popleft()

    def peek(self):
        return self._deque[0]


class SinglyLinkedListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a singly linked list."""

    __slots__ = ('_head','_len')

    # TODO: Investigate construction from iterables.
    def __init__(self):
        """Construct a SinglyLinkedListLifoQueue from an empty Sll."""
        self._head = None
        self._len = 0

    def __bool__(self):
        return bool(self._head)

    def __len__(self):
        return self._len

    def enqueue(self, item):
        new_node = _Node(item)
        new_node.nextn = self._head
        self._head = new_node
        self._len += 1

    def dequeue(self):
        if self._head:
            result = self._head.value
            self._head = self._head.nextn
            self._len -= 1
            return result
        else:
            raise LookupError("Can't dequeue from empty queue")

    def peek(self):
        if self._head:
            return self._head.value
        else:
            raise LookupError("Can't peek from empty queue")


class FastEnqueueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(1) enqueue, O(n) dequeue, and O(n) peek."""

    __slots__ = ('_list',)

    def __init__(self):
        """Construct a FastEnqueueMaxPriorityQueue from an empty list."""
        self._list = []

    def __bool__(self):
        return bool(self._list)

    def __len__(self):
        return len(self._list)

    # NOTE: O(1) since list.append is O(1)
    def enqueue(self, item):
        self._list.append(item)

    # NOTE: O(n) due to max and remove
    def dequeue(self):
        if self._list:
            result = max(self._list)
            self._list.remove(result)
            return result
        raise LookupError("Can't dequeue from empty queue")

    # NOTE: O(n) due to max
    def peek(self):
        if self._list:
            return max(self._list)
        raise LookupError("Can't peek from empty queue")


class FastDequeueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(n) enqueue, O(1) dequeue, and O(1) peek."""

    __slots__ = ('_deque',)

    def __init__(self):
        """Construct a FastDequeueMaxPriorityQueue from an empty list."""
        self._deque = []

    def __bool__(self):
        return bool(self._deque)

    def __len__(self):
        return len(self._deque)

    # NOTE: At least O(n) because of insert and loop iteration
    def enqueue(self, item):
        if not self._deque or item >= self._deque[-1]:
            self._deque.append(item)
        else:
            for index, element in enumerate(self._deque):
                if element > item:
                    self._deque.insert(index, item)
                    break

    # NOTE: List.pop is O(1)
    def dequeue(self):
        if self._deque:
            return self._deque.pop()
        raise LookupError("Can't dequeue from empty queue")

    # NOTE: Indexing into a list is O(1)
    def peek(self):
        if self._deque:
            return self._deque[-1]
        raise LookupError("Can't peek from empty queue")


class _Node:
    """Singly linked list node for FIFO and LIFO queues."""

    __slots__ = ('_value', 'nextn')

    def __init__(self, value, nextn=None):
        self._value = value
        self.nextn = nextn

    def __repr__(self):
        return f"{type(self).__name__}({self._value!r}, {self.nextn!r})"

    @property
    def value(self):
        """The value of this node."""
        return self._value
