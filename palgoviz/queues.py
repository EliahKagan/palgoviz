# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of these queue types might not override __repr__. Eventually,
that should be fixed (and this note removed). Design decisions to accompany
implementing __repr__ might include: Should (all or some of) the queue types
support construction from an iterable? Be iterable themselves? Reversible?
Should distinct queue objects ever be equal? To objects of a different type?

TODO: In particular, explore construction from iterables.
"""

__all__ = [
    'Queue',
    'FifoQueue',
    'LifoQueue',
    'PriorityQueue',
    'DequeFifoQueue',
    'AltDequeFifoQueue',
    'SlowFifoQueue',
    'BiStackFifoQueue',
    'SinglyLinkedListFifoQueue',
    'ListLifoQueue',
    'DequeLifoQueue',
    'AltDequeLifoQueue',
    'SinglyLinkedListLifoQueue',
    'FastEnqueueMaxPriorityQueue',
    'FastDequeueMaxPriorityQueue',
]

from abc import ABC, abstractmethod
import bisect
import collections
import operator


class Queue(ABC):
    """Abstract class representing a generalized queue."""

    __slots__ = ()

    @abstractmethod
    def __bool__(self):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def enqueue(self, item):
        raise NotImplementedError

    @abstractmethod
    def dequeue(self):
        raise NotImplementedError

    @abstractmethod
    def peek(self):
        raise NotImplementedError


class FifoQueue(Queue):
    """Abstract class representing a first-in first-out queue (a "queue")."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Create a FifoQueue instance."""
        return DequeFifoQueue() if cls is FifoQueue else cls()


class LifoQueue(Queue):
    """Abstract class representing a last-in first-out queue (a stack)."""

    __slots__ = ()

    @classmethod
    def create(cls):
        """Create a LifoQueue instance."""
        return ListLifoQueue() if cls is LifoQueue else cls()


class PriorityQueue(Queue):
    """Abstract class representing a priority queue."""

    __slots__ = ()

    # TODO: Explore which PriorityQueue should be default. (If we implement a
    #       binary heap in this module, then that should be the default.)
    @classmethod
    def create(cls):
        """Create a PriorityQueue instance."""
        return FastEnqueueMaxPriorityQueue() if cls is PriorityQueue else cls()


class DequeFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a collections.deque."""

    __slots__ = ('_deque',)

    def __init__(self):
        """Construct a DequeFifoQueue using a deque."""
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

    def __init__(self):
        """Construct an AltDequeFifoQueue using a deque."""
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

    def __init__(self):
        """Construct a SlowFifoQueue using a list."""
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

    __slots__ = ('_out', '_in')

    def __init__(self):
        """Construct a BiStackFifoQueue using lists."""
        self._out = []
        self._in = []

    def __bool__(self):
        return bool(self._out or self._in)

    def __len__(self):
        return len(self._out) + len(self._in)

    def enqueue(self, item):
        self._in.append(item)

    def dequeue(self):
        if not self:
            raise LookupError("Can't dequeue from empty queue")

        if not self._out:
            while self._in:
                self._out.append(self._in.pop())

        return self._out.pop()

    def peek(self):
        if not self:
            raise LookupError("Can't peek from empty queue")

        return self._out[-1] if self._out else self._in[0]


class SinglyLinkedListFifoQueue(FifoQueue):
    """A FIFO queue (i.e., a "queue") based on a singly linked list."""

    __slots__ = ('_head', '_tail', '_len')

    def __init__(self):
        """Construct a SinglyLinkedListFifoQueue, that will use SLL nodes."""
        self._head = self._tail = None
        self._len = 0

    def __bool__(self):
        return bool(self._head)

    def __len__(self):
        return self._len

    def enqueue(self, item):
        if not self._head:
            self._head = self._tail = _Node(item)
        else:
            self._tail.nextn = _Node(item)
            self._tail = self._tail.nextn
        self._len += 1

    def dequeue(self):
        if not self._head:
            raise LookupError("Can't dequeue from empty queue")

        result = self._head.value

        if self._len == 1:
            self._head = self._tail = None
        else:
            self._head = self._head.nextn

        self._len -= 1
        return result

    def peek(self):
        if not self._head:
            raise LookupError("Can't peek from empty queue")
        return self._head.value


class ListLifoQueue(LifoQueue):
    """A LIFO queue (i.e., a stack) based on a list."""

    __slots__ = ('_list',)

    def __init__(self):
        """Construct a ListLifoQueue using a list."""
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

    def __init__(self):
        """Construct a DequeLifoQueue using a deque."""
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

    def __init__(self):
        """Construct an AltDequeLifoQueue using a deque."""
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

    __slots__ = ('_head', '_len')

    def __init__(self):
        """Construct a SinglyLinkedListLifoQueue, that will use SLL nodes."""
        self._head = None
        self._len = 0

    def __bool__(self):
        return bool(self._head)

    def __len__(self):
        return self._len

    def enqueue(self, item):
        self._head = _Node(item, self._head)
        self._len += 1

    def dequeue(self):
        if not self._head:
            raise LookupError("Can't dequeue from empty queue")

        result = self._head.value
        self._head = self._head.nextn
        self._len -= 1
        return result

    def peek(self):
        if not self._head:
            raise LookupError("Can't peek from empty queue")
        return self._head.value


class FastEnqueueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(1) enqueue, O(n) dequeue, and O(n) peek."""

    __slots__ = ('_list',)

    def __init__(self):
        """Construct a FastEnqueueMaxPriorityQueue using a list."""
        self._list = []

    def __bool__(self):
        return bool(self._list)

    def __len__(self):
        return len(self._list)

    def enqueue(self, item):
        self._list.append(item)

    def dequeue(self):
        if not self:
            raise LookupError("Can't dequeue from empty queue")
        index, _ = max(enumerate(self._list), key=operator.itemgetter(1))
        self._list[index], self._list[-1] = self._list[-1], self._list[index]
        return self._list.pop()

    def peek(self):
        if not self:
            raise LookupError("Can't peek from empty queue")
        return max(self._list)


class FastDequeueMaxPriorityQueue(PriorityQueue):
    """A max priority queue with O(n) enqueue, O(1) dequeue, and O(1) peek."""

    __slots__ = ('_list',)

    def __init__(self):
        """Construct a FastDequeueMaxPriorityQueue using a list."""
        self._list = []

    def __bool__(self):
        return bool(self._list)

    def __len__(self):
        return len(self._list)

    def enqueue(self, item):
        bisect.insort(self._list, item)

    def dequeue(self):
        if not self:
            raise LookupError("Can't dequeue from empty queue")
        return self._list.pop()

    def peek(self):
        if not self:
            raise LookupError("Can't peek from empty queue")
        return self._list[-1]


class _Node:
    """Singly linked list node for FIFO and LIFO queues."""

    __slots__ = ('_value', 'nextn')

    def __init__(self, value, nextn=None):
        """Construct an SLL Node."""
        self._value = value
        self.nextn = nextn

    def __repr__(self):
        return f"{type(self).__name__}({self._value!r}, {self.nextn!r})"

    @property
    def value(self):
        """The value of this node."""
        return self._value
