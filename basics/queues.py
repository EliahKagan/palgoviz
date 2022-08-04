"""
Queues, in the general sense.

TODO: To focus on fundamental operations of generalized queues, the initial
implementations of these queue types might not override __repr__. Eventually,
that should be fixed (and this note removed). Design decisions to accompany
implementing __repr__ might include: Should (all or some of) the queue types
support construction from an iterable? Be iterable themselves? Reversible?
Should distinct queue objects ever be equal? To objects of a different type?

TODO: In particular, investigate construction from iterables.
"""

from abc import ABC, abstractmethod
import bisect
import collections
import operator

import graphviz


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

    # TODO: Investigate which PriorityQueue should be default.
    @classmethod
    def create(cls):
        """Create a PriorityQueue instance."""
        return FastEnqueueMaxPriorityQueue() if cls is PriorityQueue else cls()


class DequeFifoQueue(FifoQueue):
    """A FIFO queue (i.e. a "queue") based on a collections.deque."""

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
    A FIFO queue (i.e. a "queue") based on a collections.deque.

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
    """A FIFO queue (i.e. a "queue") based on a list. Linear-time dequeue."""

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
    """A FIFO queue (i.e. a "queue") based on two lists used as stacks."""

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


class RingFifoQueue(FifoQueue):
    """
    A FIFO queue (i.e. a "queue") based on a list. All operations O(1).

    This uses a single list as a buffer: at all times, except possibly while a
    method is running, all but O(1) space belongs to a single list object.
    Methods may sometimes replace it with a new list, but if so, the old list
    is eligible to be garbage collected on return. (Methods may make as many
    lists as they like, if they abandon all but one.)

    Enqueue takes amortized O(1) time, but strictly O(1) unless the queue grows
    larger than it ever has before. Dequeue and peek take strictly O(1) time.
    Space complexity is linear in the maximum length the queue has reached.
    """

    __slots__ = ('__buffer', '__front', '__len')

    _INITIAL_CAPACITY = 1
    """The size the buffer is grown to from zero."""

    _GROWTH_FACTOR = 2
    """
    Multiplier by which capacity is increased.

    This is a protected constant: this and derived classes may read its value.
    """

    __ABSENT = object()
    """Sentinel representing the absence of an item, so debugging is easier."""

    def __init__(self):
        """Construct a RingFifoQueue, which uses a single list as a buffer."""
        self.__buffer = []
        self.__front = self.__len = 0

    def __bool__(self):
        return self.__len != 0

    def __len__(self):
        return self.__len

    def enqueue(self, item):
        assert item is not self.__ABSENT

        self.__ensure_capacity()
        index = (self.__front + self.__len) % self._capacity
        assert self.__buffer[index] is self.__ABSENT
        self.__buffer[index] = item
        self.__len += 1

    def dequeue(self):
        item = self.__do_peek("Can't dequeue from empty queue")
        self.__buffer[self.__front] = self.__ABSENT
        self.__front = (self.__front + 1) % self._capacity
        self.__len -= 1
        return item

    def peek(self):
        return self.__do_peek("Can't peek from empty queue")

    @property
    def _capacity(self):
        """
        The maximum length the current buffer can hold without being expanded.

        This is a protected property: only this and derived classes may use it.
        """
        return len(self.__buffer)

    def _resize_buffer(self, new_capacity):
        """
        Change the buffer capacity.

        This is a protected method: only this and derived classes may use it.
        """
        if new_capacity < self.__len:
            raise ValueError(
                f'capacity {new_capacity!r} less than length {self.__len!r}')

        end1 = min(self.__front + self.__len, self._capacity)
        end2 = max(0, self.__len - (end1 - self.__front))  # Wrap around.

        self.__buffer = (self.__buffer[self.__front:end1] + self.__buffer[:end2]
                        + [self.__ABSENT] * (new_capacity - self.__len))
        self.__front = 0  # TODO: Ensure tests catch if this is omitted.

        assert self._capacity == new_capacity

    def __ensure_capacity(self):
        if self.__len < self._capacity:
            return

        assert self.__len == self._capacity

        if self.__len == 0:
            self._resize_buffer(self._INITIAL_CAPACITY)
        else:
            self._resize_buffer(self.__len * self._GROWTH_FACTOR)

    def __do_peek(self, fail_message):
        if not self:
            raise LookupError(fail_message)
        item = self.__buffer[self.__front]
        assert item is not self.__ABSENT
        return item


class CompactRingFifoQueue(RingFifoQueue):
    """
    A FIFO queue (i.e. a "queue") based on a list. O(1) operations. O(n) space.

    This derives from RingFifoQueue and satisfies its documented guarantees,
    except time complexities for enqueue and dequeue are only amortized, and
    space is linear in the current length. Amortization does cover arbitrarily
    interleaved operations: a series of any n public method calls takes
    strictly O(n) time.

    FIXME: Ensure CompactRingFifoQueue duplicates no logic from RingFifoQueue,
    and that encapsulation is never violated. You can add protected members to
    RingFifoQueue to facilitate the operations CompactRingFifoQueue requires to
    meet its time and space guarantees, but only if (i) they would be broadly
    useful to derived classes, not specific to CompactRingFifoQueue, (ii) some
    public methods of RingFifoQueue are modified to use them, and code quality
    is preserved or improved, (iii) separation is preserved, so derived classes
    rely minimally or not at all on implementation details of RingFifoQueue,
    and (iv) encapsulation is preserved, so derived classes aren't given power
    that wouldn't tend to be useful, and the protected interface can't be used
    to corrupt any data managed by the base class (without deliberate effort).
    If this doesn't hold initially, that's OK, but please revise to satisfy it.
    """

    __slots__ = ()

    _SHRINK_TRIGGER = RingFifoQueue._GROWTH_FACTOR * 2
    """Capacity is decreased when it is this many times the length in use."""

    def dequeue(self):
        item = super().dequeue()
        if len(self) * self._SHRINK_TRIGGER <= self._capacity:
            self._resize_buffer(len(self))
        return item


class SinglyLinkedListFifoQueue(FifoQueue):
    """A FIFO queue (i.e. a "queue") based on a singly linked list."""

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

    def copy(self):
        """
        Create a SinglyLinkedListFifoQueue that is a copy of this one.

        This may be called any number of times, including on copies. Operations
        on an instance do not affect any copies or originals related to it.

        The time complexity to copy is [FIXME: state it]. A series of k
        operations, each of which constructs or calls a public method on some
        SinglyLinkedListFifoQueue instance, takes [FIXME: how long?] and uses
        [FIXME: how much space?] in the worst case. These are the best this
        concrete data structure can do, due to how it represents data.
        """
        dup = type(self)()

        node = self._head
        while node:
            dup.enqueue(node.value)
            node = node.nextn

        return dup


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

    def copy(self):
        """
        Create a SinglyLinkedListLifoQueue that is a copy of this one.

        This may be called any number of times, including on copies. Operations
        on an instance do not affect any copies or originals related to it.

        Copying takes [FIXME: how much?] time. Any series of k operations, each
        constructing a SinglyLinkedListLifoQueue or calling a public method
        (other than draw) on a SinglyLinkedListLifoQueue, takes [FIXME: how
        much?] time and uses [FIXME: how much?] space in the worst case. These
        are the best this concrete data structure can do, due to how it
        represents data.
        """
        dup = type(self)()
        dup._head = self._head
        dup._len = self._len
        return dup

    # !!FIXME: When removing implementation bodies, change "def draw(*queues):"
    # to: "def draw():  # FIXME: Fill in your function parameters."
    def draw(*queues):
        """
        Visualize how zero or more SinglyLinkedLifoQueues are/aren't related.

        Copying a SinglyLinkedListLifoQueue is more efficient than copying a
        SinglyLinkedListFifoQueue, in a way that makes it interesting to
        visualize the state of multiple SinglyLinkedListLifoQueue instances if
        some may have been created by copying others.

        This creates and returns such a drawing as a graphviz.Digraph. This
        method can be called with static method syntax or instance method
        syntax. For example, SinglyLinkedListLifoQueue.draw() draws zero
        queues, SinglyLinkedListLifoQueue.draw(a, b, c) draws three queues, and
        a.draw(b, c) draws those same three queues.

        Some such drawings can be seen in [FIXME: say where you put them, which
        should probably be queues.ipynb].
        """
        vis = {None}
        graph = graphviz.Digraph()

        for queue in queues:
            parent = None
            child = queue._head

            while child:
                if child not in vis:
                    graph.node(str(id(child)), label=repr(child.value))
                if parent:
                    graph.edge(str(id(parent)), str(id(child)))
                if child in vis:
                    break
                vis.add(child)
                parent, child = child, child.nextn

        return graph


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
