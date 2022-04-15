#!/usr/bin/env python

"""
Tests for queues.py.

TODO: These tests are currently organized in such a way that test runners group
them by shared behavior. Modify this file so test runners instead group them by
what class is being tested. But do it without a major change to the testing
logic and organization in this file. In particular, retain the meaning and
order of all currently existing test classes, as well as the names, meaning,
and order of all test methods in each currently existing test class. (But if
you prefer it this way after doing so, please feel free to revert the change.)
"""

import inspect
import unittest

from parameterized import parameterized, parameterized_class

import queues


def _unannotated_argspec(func):
    """Get the full argspec of a callable object, but without annotations."""
    return inspect.getfullargspec(func)[:6]


@parameterized_class(('name', 'queue_type'), [
    ('Queue', queues.Queue),
    ('FifoQueue', queues.FifoQueue),
    ('LifoQueue', queues.LifoQueue),
    ('PriorityQueue', queues.PriorityQueue),
])
class TestAbstract(unittest.TestCase):
    """Tests for abstract queue types."""

    def test_is_abstract(self):
        self.assertTrue(inspect.isabstract(self.queue_type))

    def test_abstract_methods_are_bool_len_enqueue_dequeue_peek(self):
        expected = {'__bool__', '__len__', 'enqueue', 'dequeue', 'peek'}
        actual = self.queue_type.__abstractmethods__
        self.assertSetEqual(actual, expected)


@parameterized_class(('name', 'queue_type'), [
    ('Queue', queues.Queue),
    ('FifoQueue', queues.FifoQueue),
    ('LifoQueue', queues.LifoQueue),
    ('PriorityQueue', queues.PriorityQueue),
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
    ('SinglyLinkedListFifoQueue', queues.SinglyLinkedListFifoQueue),
    ('ListLifoQueue', queues.ListLifoQueue),
    ('DequeLifoQueue', queues.DequeLifoQueue),
    ('AltDequeLifoQueue', queues.AltDequeLifoQueue),
    ('SinglyLinkedListLifoQueue', queues.SinglyLinkedListLifoQueue),
    ('FastEnqueueMaxPriorityQueue', queues.FastEnqueueMaxPriorityQueue),
    ('FastDequeueMaxPriorityQueue', queues.FastDequeueMaxPriorityQueue),
])
class TestSignatures(unittest.TestCase):
    """Tests for expected queue methods. All queue types should pass these."""

    def test_bool_method_has_data_model_recommended_signature(self):
        """The __bool__ method accepts no arguments (besides self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(self.queue_type.__bool__)
        self.assertTupleEqual(actual, expected)

    def test_len_method_has_data_model_recommended_signature(self):
        """The __len__ method accepts no arguments (besides self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(self.queue_type.__len__)
        self.assertTupleEqual(actual, expected)

    def test_enqueue_method_has_item_parameter_and_no_extras(self):
        """The enqueue method accepts only an item argument (and self)."""
        expected = (['self', 'item'], None, None, None, [], None)
        actual = _unannotated_argspec(self.queue_type.enqueue)
        self.assertTupleEqual(actual, expected)

    def test_dequeue_method_has_no_extra_parameters(self):
        """The dequeue method accepts no arguments (except self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(self.queue_type.dequeue)
        self.assertTupleEqual(actual, expected)

    def test_peek_method_has_no_extra_parameters(self):
        """The peek method accepts no arguments (except self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(self.queue_type.peek)
        self.assertTupleEqual(actual, expected)


@parameterized_class(('name', 'queue_type'), [
    ('FifoQueue', queues.FifoQueue),
    ('LifoQueue', queues.LifoQueue),
    ('PriorityQueue', queues.PriorityQueue),
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
    ('SinglyLinkedListFifoQueue', queues.SinglyLinkedListFifoQueue),
    ('ListLifoQueue', queues.ListLifoQueue),
    ('DequeLifoQueue', queues.DequeLifoQueue),
    ('AltDequeLifoQueue', queues.AltDequeLifoQueue),
    ('SinglyLinkedListLifoQueue', queues.SinglyLinkedListLifoQueue),
    ('FastEnqueueMaxPriorityQueue', queues.FastEnqueueMaxPriorityQueue),
    ('FastDequeueMaxPriorityQueue', queues.FastDequeueMaxPriorityQueue),
])
class TestSubclasses(unittest.TestCase):
    """Tests for leaf and non-leaf subclasses of Queue."""

    def test_is_queue(self):
        """All queue classes are subclasses of Queue."""
        self.assertTrue(issubclass(self.queue_type, queues.Queue))

    def test_create_creates_instance_of_class_it_is_called_on(self):
        """
        Calling create on a queue class creates an instance of that class.

        It need not be a direct instance. When the class it is called on is
        abstract, it will not be a direct instance. (Currently the abstract
        queue classes with create() methods are FifoQueue and LifoQueue.)
        """
        queue = self.queue_type.create()
        self.assertIsInstance(queue, self.queue_type)

    def test_create_creates_empty_instance(self):
        """create() methods return queues that are falsy, thus empty."""
        queue = self.queue_type.create()
        self.assertFalse(queue)


@parameterized_class(('name', 'queue_type'), [
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
    ('SinglyLinkedListFifoQueue', queues.SinglyLinkedListFifoQueue),
    ('ListLifoQueue', queues.ListLifoQueue),
    ('DequeLifoQueue', queues.DequeLifoQueue),
    ('AltDequeLifoQueue', queues.AltDequeLifoQueue),
    ('SinglyLinkedListLifoQueue', queues.SinglyLinkedListLifoQueue),
    ('FastEnqueueMaxPriorityQueue', queues.FastEnqueueMaxPriorityQueue),
    ('FastDequeueMaxPriorityQueue', queues.FastDequeueMaxPriorityQueue),
])
class TestConcrete(unittest.TestCase):
    """Tests for concrete queue types."""

    def test_falsy_on_creation(self):
        """A new queue is empty, and thus false."""
        queue = self.queue_type()
        self.assertFalse(queue)

    def test_length_zero_on_creation(self):
        """A new queue is empty, and thus has exactly zero items."""
        queue = self.queue_type()
        length = len(queue)
        self.assertEqual(length, 0)

    def test_truthy_after_enqueue(self):
        """A queue with an element in it is nonempty, and thus true."""
        queue = self.queue_type()
        queue.enqueue('ham')
        self.assertTrue(queue)

    def test_length_1_after_enqueue(self):
        """After exactly 1 enqueue and no dequeues, a queue has 1 item."""
        queue = self.queue_type()
        queue.enqueue('ham')
        length = len(queue)
        self.assertEqual(length, 1)

    def test_falsy_after_enqueue_dequeue(self):
        """After exactly 1 enqueue and dequeue, a queue is false again."""
        queue = self.queue_type()
        queue.enqueue('ham')
        queue.dequeue()
        self.assertFalse(queue)

    def test_length_0_after_enqueue_dequeue(self):
        """After exactly 1 enqueue and dequeue, a queue has 0 items."""
        queue = self.queue_type()
        queue.enqueue('ham')
        queue.dequeue()
        length = len(queue)
        self.assertEqual(length, 0)

    def test_truthy_after_enqueue_peek(self):
        """
        After only enqueue and peek, a queue is nonempty, thus true.

        Calling peek shouldn't modify the queue, so it shouldn't make it empty.
        """
        queue = self.queue_type()
        queue.enqueue('ham')
        queue.peek()
        self.assertTrue(queue)

    def test_length_1_after_enqueue_peek(self):
        """
        After only enqueue and peek, a queue still has exactly 1 item.

        Calling peek shouldn't modify the queue, including its size.
        """
        queue = self.queue_type()
        queue.enqueue('ham')
        queue.peek()
        length = len(queue)
        self.assertEqual(length, 1)

    def test_singleton_queue_dequeues_enqueued_item(self):
        """After exactly 1 enqueue, a dequeue gives the enqueued item."""
        queue = self.queue_type()
        queue.enqueue('ham')
        dequeued_item = queue.dequeue()
        self.assertEqual(dequeued_item, 'ham')

    def test_singleton_queue_peeks_enqueued_item(self):
        """After exactly 1 enqueue, a peek reveals the enqueued item."""
        queue = self.queue_type()
        queue.enqueue('ham')
        peeked_item = queue.peek()
        self.assertEqual(peeked_item, 'ham')

    def test_cannot_dequeue_from_empty_queue(self):
        """
        When a queue is empty, attempting to dequeue raises LookupError.

        NOTE: Usually the LookupError subclass IndexError should be raised.
        """
        queue = self.queue_type()

        # Give error result (not mere fail) if queue is somehow nonempty.
        if queue:
            raise Exception("new queue is truthy, can't continue")
        if len(queue) != 0:
            raise Exception("new queue has nonzero len, can't continue")

        with self.assertRaises(LookupError):
            queue.dequeue()

    def test_cannot_peek_from_empty_queue(self):
        """
        When a queue is empty, attempting to peek raises LookupError.

        NOTE: Usually the LookupError subclass IndexError should be raised.
        """
        queue = self.queue_type()

        # Give error result (not mere fail) if queue is somehow nonempty.
        if queue:
            raise Exception("new queue is truthy, can't continue")
        if len(queue) != 0:
            raise Exception("new queue has nonzero len, can't continue")

        with self.assertRaises(LookupError):
            queue.peek()

    @parameterized.expand([
        ('distinct strings',
         ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']),
        ('distinct numbers', range(0, 1000, 10)),
        ('distinct tuples', [(10, 20), (31, 17), (9, 87), (-14, 2)]),
        ('distinct lists', [list(range(n)) for n in range(10)]),
        ('identical lists', [['a', 'parrot']] * 10),
        ('equal lists', [['a', 'parrot'] for _ in range(10)]),
        ('not-all-distinct sets', [{'ab', 'cd'}, {'ab', 'cd'}, set()]),
    ])
    def test_dequeuing_gives_enqueued_items_in_some_order(self,
                                                          _label,
                                                          in_items):
        queue = self.queue_type()

        for item in in_items:
            queue.enqueue(item)

        out_items = []
        while queue:
            out_items.append(queue.dequeue())

        self.assertListEqual(sorted(in_items), sorted(out_items))


@parameterized_class(('name', 'queue_type'), [
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
    ('SinglyLinkedListFifoQueue', queues.SinglyLinkedListFifoQueue),
])
class TestFifos(unittest.TestCase):
    """Tests for concrete FIFO queue ("queue") behavior."""

    def test_is_fifoqueue(self):
        """FIFO queue classes are subclasses of FifoQueue."""
        self.assertTrue(issubclass(self.queue_type, queues.FifoQueue))

    def test_first_dequeues_before_second(self):
        """When two items are enqueued, they dequeue in the same order."""
        fifo = self.queue_type()
        fifo.enqueue('ham')
        fifo.enqueue('spam')

        with self.subTest(dequeue=1):
            item = fifo.dequeue()
            self.assertEqual(item, 'ham')

        with self.subTest(dequeue=2):
            item = fifo.dequeue()
            self.assertEqual(item, 'spam')

    def test_peek_reveals_oldest_not_yet_dequeued(self):
        """After two enqueues, peek always shows what should dequeue."""
        fifo = self.queue_type()
        fifo.enqueue('ham')
        fifo.enqueue('spam')

        with self.subTest(peek=1):
            item = fifo.peek()
            self.assertEqual(item, 'ham')

        fifo.dequeue()

        with self.subTest(peek=2):
            item = fifo.peek()
            self.assertEqual(item, 'spam')

    def test_mixed_enqueues_and_dequeues_dequeue_in_fifo_order(self):
        """Interleaved operations behave properly as a "queue"."""
        fifo = self.queue_type()
        fifo.enqueue(10)
        fifo.enqueue(30)
        fifo.enqueue(20)

        with self.subTest(size=len(fifo), dequeue=1):
            item = fifo.dequeue()
            self.assertEqual(item, 10)

        with self.subTest(size=len(fifo), dequeue=2):
            item = fifo.dequeue()
            self.assertEqual(item, 30)

        fifo.enqueue(50)
        fifo.enqueue(40)

        with self.subTest(size=len(fifo), dequeue=3):
            item = fifo.dequeue()
            self.assertEqual(item, 20)

        fifo.enqueue(60)

        with self.subTest(size=len(fifo), dequeue=4):
            item = fifo.dequeue()
            self.assertEqual(item, 50)

        with self.subTest(size=len(fifo), dequeue=5):
            item = fifo.dequeue()
            self.assertEqual(item, 40)

        with self.subTest(size=len(fifo), dequeue=6):
            item = fifo.dequeue()
            self.assertEqual(item, 60)

    def test_mixed_enqueues_and_dequeues_peeks_in_fifo_order(self):
        """Interleaved peeks align with proper "queue"-order dequeuing."""
        fifo = self.queue_type()
        fifo.enqueue(10)
        fifo.enqueue(30)
        fifo.enqueue(20)

        with self.subTest(size=len(fifo), peek=1):
            item = fifo.peek()
            self.assertEqual(item, 10)

        fifo.dequeue()

        with self.subTest(size=len(fifo), peek=2):
            item = fifo.peek()
            self.assertEqual(item, 30)

        fifo.dequeue()
        fifo.enqueue(50)
        fifo.enqueue(40)

        with self.subTest(size=len(fifo), peek=3):
            item = fifo.peek()
            self.assertEqual(item, 20)

        fifo.dequeue()
        fifo.enqueue(60)

        with self.subTest(size=len(fifo), peek=4):
            item = fifo.peek()
            self.assertEqual(item, 50)

        fifo.dequeue()

        with self.subTest(size=len(fifo), peek=5):
            item = fifo.peek()
            self.assertEqual(item, 40)

        fifo.dequeue()

        with self.subTest(size=len(fifo), dequeue=6):
            item = fifo.peek()
            self.assertEqual(item, 60)


@parameterized_class(('name', 'queue_type'), [
    ('ListLifoQueue', queues.ListLifoQueue),
    ('DequeLifoQueue', queues.DequeLifoQueue),
    ('AltDequeLifoQueue', queues.AltDequeLifoQueue),
    ('SinglyLinkedListLifoQueue', queues.SinglyLinkedListLifoQueue),
])
class TestLifos(unittest.TestCase):
    """Tests for concrete LIFO queue (stack) behavior."""

    def test_if_lifoqueue(self):
        """LIFO queue classes are subclasses of LifoQueue."""
        self.assertTrue(issubclass(self.queue_type, queues.LifoQueue))

    def test_first_dequeues_after_second(self):
        """When two items are enqueued, they dequeue in reverse order."""
        lifo = self.queue_type()
        lifo.enqueue('ham')
        lifo.enqueue('spam')

        with self.subTest(dequeue=1):
            item = lifo.dequeue()
            self.assertEqual(item, 'spam')

        with self.subTest(dequeue=2):
            item = lifo.dequeue()
            self.assertEqual(item, 'ham')

    def test_peek_reveals_newest_not_yet_dequeued(self):
        """After two enqueues, peek always shows what should dequeue."""
        lifo = self.queue_type()
        lifo.enqueue('ham')
        lifo.enqueue('spam')

        with self.subTest(peek=1):
            item = lifo.peek()
            self.assertEqual(item, 'spam')

        lifo.dequeue()

        with self.subTest(peek=2):
            item = lifo.peek()
            self.assertEqual(item, 'ham')

    def test_mixed_enqueues_and_dequeues_dequeue_in_lifo_order(self):
        """Interleaved operations behave properly as a stack."""
        lifo = self.queue_type()
        lifo.enqueue(10)
        lifo.enqueue(30)
        lifo.enqueue(20)

        with self.subTest(len(lifo), dequeue=1):
            item = lifo.dequeue()
            self.assertEqual(item, 20)

        with self.subTest(len(lifo), dequeue=2):
            item = lifo.dequeue()
            self.assertEqual(item, 30)

        lifo.enqueue(50)
        lifo.enqueue(40)

        with self.subTest(size=len(lifo), dequeue=3):
            item = lifo.dequeue()
            self.assertEqual(item, 40)

        lifo.enqueue(60)

        with self.subTest(size=len(lifo), dequeue=4):
            item = lifo.dequeue()
            self.assertEqual(item, 60)

        with self.subTest(size=len(lifo), dequeue=5):
            item = lifo.dequeue()
            self.assertEqual(item, 50)

        with self.subTest(size=len(lifo), dequeue=6):
            item = lifo.dequeue()
            self.assertEqual(item, 10)

    def test_mixed_enqueues_and_dequeues_peeks_in_lifo_order(self):
        """Interleaved peeks align with proper stack-order dequeuing."""
        lifo = self.queue_type()
        lifo.enqueue(10)
        lifo.enqueue(30)
        lifo.enqueue(20)

        with self.subTest(len(lifo), peek=1):
            item = lifo.peek()
            self.assertEqual(item, 20)

        lifo.dequeue()

        with self.subTest(len(lifo), peek=2):
            item = lifo.peek()
            self.assertEqual(item, 30)

        lifo.dequeue()
        lifo.enqueue(50)
        lifo.enqueue(40)

        with self.subTest(size=len(lifo), peek=3):
            item = lifo.peek()
            self.assertEqual(item, 40)

        lifo.dequeue()
        lifo.enqueue(60)

        with self.subTest(size=len(lifo), peek=4):
            item = lifo.peek()
            self.assertEqual(item, 60)

        lifo.dequeue()

        with self.subTest(size=len(lifo), peek=5):
            item = lifo.peek()
            self.assertEqual(item, 50)

        lifo.dequeue()

        with self.subTest(size=len(lifo), peek=6):
            item = lifo.peek()
            self.assertEqual(item, 10)


@parameterized_class(('name', 'queue_type'), [
    ('FastEnqueueMaxPriorityQueue', queues.FastEnqueueMaxPriorityQueue),
    ('FastDequeueMaxPriorityQueue', queues.FastDequeueMaxPriorityQueue),
])
class TestPriorityQueues(unittest.TestCase):
    """
    Tests for concrete priority queues. Max priority queue behavior is assumed.

    NOTE: This API is unstable and expected to change in the near future.

    TODO: It is best for priority queue types to be versatile: able to act as
    either a min priority queue or a max priority queue, and also accepting an
    arbitrary key selector function. Therefore, no tests require presence of a
    MaxPriorityQueue abstract class, since that would not often be a good
    design. But for simplicity, our initial design involves just max priority
    queue behavior. These tests currently expect that behavior. These are max
    rather than min priority queues because that makes one of the concrete
    classes easier to implement using standard library facilities. But there is
    a good argument our priority queues should, by default, operate as min
    priority queues instead: Python programmers are likely to expect a min
    default, because the heapq module provides low-level binary minheap (not
    maxheap) operations. Eventually, we should redesign our priority queues,
    possibly changing the min/max default, and definitely having all concrete
    implementations' initializers accept key= and reverse= arguments.
    """

    def test_is_priority_queue(self):
        """Priority queue classes are subclasses of PriorityQueue."""
        self.assertTrue(issubclass(self.queue_type, queues.PriorityQueue))

    def test_dequeue_high_after_enqueue_low_high(self):
        """When 2 items are enqueued, low first, the higher dequeues first."""
        pq = self.queue_type()
        pq.enqueue('ham')
        pq.enqueue('spam')

        with self.subTest(dequeue=1):
            item = pq.dequeue()
            self.assertEqual(item, 'spam')

        with self.subTest(dequeue=2):
            item = pq.dequeue()
            self.assertEqual(item, 'ham')

    def test_dequeue_high_after_enqueue_high_low(self):
        """When 2 items are enqueued, high first, the higher dequeues first."""
        pq = self.queue_type()
        pq.enqueue('spam')
        pq.enqueue('ham')

        with self.subTest(dequeue=1):
            item = pq.dequeue()
            self.assertEqual(item, 'spam')

        with self.subTest(dequeue=2):
            item = pq.dequeue()
            self.assertEqual(item, 'ham')

    def test_peek_high_after_enqueue_low_high(self):
        """When 2 items are enqueued, low first, peek returns the second."""
        pq = self.queue_type()
        pq.enqueue('ham')
        pq.enqueue('spam')

        with self.subTest(peek=1):
            item = pq.peek()
            self.assertEqual(item, 'spam')

        pq.dequeue()

        with self.subTest(peek=2):
            item = pq.peek()
            self.assertEqual(item, 'ham')

    def test_peek_high_after_enqueue_high_low(self):
        """When 2 items are enqueued, high first, peek returns the first."""
        pq = self.queue_type()
        pq.enqueue('spam')
        pq.enqueue('ham')

        with self.subTest(peek=1):
            item = pq.peek()
            self.assertEqual(item, 'spam')

        pq.dequeue()

        with self.subTest(peek=2):
            item = pq.peek()
            self.assertEqual(item, 'ham')

    def test_mixed_enqueues_and_dequeues_always_dequeue_max(self):
        """Interleaved operations behave properly as a max priority queue."""
        pq = self.queue_type()
        pq.enqueue(10)
        pq.enqueue(30)
        pq.enqueue(20)

        with self.subTest(size=len(pq), dequeue=1):
            item = pq.dequeue()
            self.assertEqual(item, 30)

        with self.subTest(size=len(pq), dequeue=2):
            item = pq.dequeue()
            self.assertEqual(item, 20)

        pq.enqueue(50)
        pq.enqueue(40)

        with self.subTest(size=len(pq), dequeue=3):
            item = pq.dequeue()
            self.assertEqual(item, 50)

        pq.enqueue(60)

        with self.subTest(size=len(pq), dequeue=4):
            item = pq.dequeue()
            self.assertEqual(item, 60)

        with self.subTest(size=len(pq), dequeue=5):
            item = pq.dequeue()
            self.assertEqual(item, 40)

        with self.subTest(size=len(pq), dequeue=6):
            item = pq.dequeue()
            self.assertEqual(item, 10)

    def test_mixed_enqueues_and_dequeues_always_peek_max(self):
        """
        Interleaved peeks align with proper max priority queue order dequeuing.
        """
        pq = self.queue_type()
        pq.enqueue(10)
        pq.enqueue(30)
        pq.enqueue(20)

        with self.subTest(size=len(pq), peek=1):
            item = pq.peek()
            self.assertEqual(item, 30)

        pq.dequeue()

        with self.subTest(size=len(pq), peek=2):
            item = pq.peek()
            self.assertEqual(item, 20)

        pq.dequeue()
        pq.enqueue(50)
        pq.enqueue(40)

        with self.subTest(size=len(pq), peek=3):
            item = pq.peek()
            self.assertEqual(item, 50)

        pq.dequeue()
        pq.enqueue(60)

        with self.subTest(size=len(pq), peek=4):
            item = pq.peek()
            self.assertEqual(item, 60)

        pq.dequeue()

        with self.subTest(size=len(pq), peek=5):
            item = pq.peek()
            self.assertEqual(item, 40)

        pq.dequeue()

        with self.subTest(size=len(pq), dequeue=6):
            item = pq.peek()
            self.assertEqual(item, 10)


if __name__ == '__main__':
    unittest.main()
