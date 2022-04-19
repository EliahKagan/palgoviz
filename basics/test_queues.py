#!/usr/bin/env python

"""Tests for queues.py."""

from abc import ABC, abstractmethod
import inspect
import unittest

from parameterized import parameterized

import compare
import queues


def _unannotated_argspec(func):
    """Get the full argspec of a callable object, but without annotations."""
    return inspect.getfullargspec(func)[:6]


class _Bases:
    """Base classes for tests for queues module."""

    class _QueueTestCase(ABC, unittest.TestCase):
        @property
        @abstractmethod
        def queue_type(self):
            """The queue type being tested."""

    class TestAbstract(_QueueTestCase):
        """Tests for abstract queue types."""

        def test_is_abstract(self):
            self.assertTrue(inspect.isabstract(self.queue_type))

        def test_abstract_methods_are_bool_len_enqueue_dequeue_peek(self):
            expected = {'__bool__', '__len__', 'enqueue', 'dequeue', 'peek'}
            actual = self.queue_type.__abstractmethods__
            self.assertSetEqual(actual, expected)

    class TestSignatures(_QueueTestCase):
        """
        Tests for expected queue methods. All queue types should pass these.
        """

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

    class TestSubclasses(_QueueTestCase):
        """Tests for leaf and non-leaf subclasses of Queue."""

        def test_is_queue(self):
            """All queue classes are subclasses of Queue."""
            self.assertTrue(issubclass(self.queue_type, queues.Queue))

        def test_create_creates_instance_of_class_it_is_called_on(self):
            """
            Calling create on a queue class creates an instance of that class.

            It need not be a direct instance. When the class it is called on is
            abstract, it will not be a direct instance. (Currently the abstract
            queue classes with create() methods are FifoQueue, LifoQueue, and
            PriorityQueue.)
            """
            queue = self.queue_type.create()
            self.assertIsInstance(queue, self.queue_type)

        def test_create_creates_empty_instance(self):
            """create() methods return queues that are falsy, thus empty."""
            queue = self.queue_type.create()
            self.assertFalse(queue)

    class TestConcrete(_QueueTestCase):
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

            Calling peek shouldn't modify the queue, so it shouldn't make it
            empty.
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

        def test_repeated_singleton_queue_dequeues_enqueued_item(self):
            """After an enqueue, dequeue, and enqueue, dequeue still works."""
            queue = self.queue_type()
            queue.enqueue('ham')
            queue.dequeue()
            queue.enqueue('spam')
            dequeued_item = queue.dequeue()
            self.assertEqual(dequeued_item, 'spam')

        def test_repeated_singleton_queue_peeks_enqueued_item(self):
            """After an enqueue, dequeue, and enqueue, peek works."""
            queue = self.queue_type()
            queue.enqueue('ham')
            queue.dequeue()
            queue.enqueue('spam')
            peeked_item = queue.peek()
            self.assertEqual(peeked_item, 'spam')

        def test_cannot_dequeue_from_empty_queue(self):
            """
            When a queue is empty, attempting to dequeue raises LookupError.

            It is allowed, and often preferable, to raise an instance of a
            suitable subclass of LookupError, such as IndexError.
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

            It is allowed, and often preferable, to raise an instance of a
            suitable subclass of LookupError, such as IndexError.
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
            """Items that can come out are all those that went in."""
            queue = self.queue_type()

            for item in in_items:
                queue.enqueue(item)

            out_items = []
            while queue:
                out_items.append(queue.dequeue())

            self.assertListEqual(sorted(out_items), sorted(in_items))

        def test_cannot_create_new_attributes(self):
            """Assigning to a nonexistent attribute raises AttributeError."""
            queue = self.queue_type()
            with self.assertRaises(AttributeError):
                queue.blah_blah_hopefully_not_an_existing_attribute_name = 42

    class TestFifos(_QueueTestCase):
        """Tests for concrete FIFO queue ("queue") behavior."""

        def test_is_fifo_queue(self):
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

        @parameterized.expand([
            ('distinct 5',
             ['e', 'd', 'c', 'a', 'b'],
             ['e', 'd', 'c', 'a', 'b']),
            ('distinct 12',
             [5, 6, 1, 10, 2, 9, 3, 8, 4, 7, 12, 11],
             [5, 6, 1, 10, 2, 9, 3, 8, 4, 7, 12, 11]),
            ('some dupes',
             ['foo', 'bar', 'bar', 'baz', 'foo', 'bar'],
             ['foo', 'bar', 'bar', 'baz', 'foo', 'bar']),
            ('all dupes', [3, 3, 3], [3, 3, 3]),
        ])
        def test_enqueues_then_dequeues_preserve_order(self, _label, in_items,
                                                       expected_out_items):
            """Items dequeue in enqueue order, no matter how many."""
            # Ensure error (not mere failure) if the test is itself wrong.
            if expected_out_items != in_items:
                raise Exception('bad test: expected should equal input')

            fifo = self.queue_type()

            for item in in_items:
                fifo.enqueue(item)

            out_items = []
            while fifo:
                out_items.append(fifo.dequeue())

            self.assertListEqual(out_items, expected_out_items)

    class TestLifos(_QueueTestCase):
        """Tests for concrete LIFO queue (stack) behavior."""

        def test_is_lifo_queue(self):
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

        @parameterized.expand([
            ('distinct 5',
             ['e', 'd', 'c', 'a', 'b'],
             ['b', 'a', 'c', 'd', 'e']),
            ('distinct 12',
             [5, 6, 1, 10, 2, 9, 3, 8, 4, 7, 12, 11],
             [11, 12, 7, 4, 8, 3, 9, 2, 10, 1, 6, 5]),
            ('some dupes',
             ['foo', 'bar', 'bar', 'baz', 'foo', 'bar'],
             ['bar', 'foo', 'baz', 'bar', 'bar', 'foo']),
            ('all dupes', [3, 3, 3], [3, 3, 3]),
        ])
        def test_enqueues_then_dequeues_reverse_order(self, _label, in_items,
                                                      expected_out_items):
            """Items dequeue in reverse order, no matter how many."""
            # Ensure error (not mere failure) if the test is itself wrong.
            if expected_out_items != in_items[::-1]:
                raise Exception('bad test: expected should reverse input')

            lifo = self.queue_type()

            for item in in_items:
                lifo.enqueue(item)

            out_items = []
            while lifo:
                out_items.append(lifo.dequeue())

            self.assertListEqual(out_items, expected_out_items)

    class TestPriorityQueues(_QueueTestCase):
        """
        Tests for concrete priority queues.

        Expects max priority queue behavior.

        NOTE: This API is unstable and expected to change in the near future.

        TODO: It is best for priority queue types to be versatile: able to act
        as either a min priority queue or a max priority queue, and also
        accepting an arbitrary key selector function. Therefore, no tests
        require presence of a MaxPriorityQueue abstract class, since that would
        not often be a good design. But for simplicity, our initial design
        involves just max priority queue behavior. These tests currently expect
        that behavior. These are max rather than min priority queues because
        that makes one of the concrete classes easier to implement using
        standard library facilities. But there is a good argument our priority
        queues should, by default, operate as min priority queues instead:
        Python programmers are likely to expect a min default, because the
        heapq module provides low-level binary minheap (not maxheap)
        operations. Eventually, we should redesign our priority queues,
        possibly changing the min/max default, and definitely having all
        concrete implementations' initializers accept key= and reverse=
        arguments.
        """

        def test_is_priority_queue(self):
            """Priority queue classes are subclasses of PriorityQueue."""
            self.assertTrue(issubclass(self.queue_type, queues.PriorityQueue))

        def test_dequeue_high_after_enqueue_low_high(self):
            """
            When 2 items are enqueued, low first, the higher dequeues first.
            """
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
            """
            When 2 items are enqueued, high first, the higher dequeues first.
            """
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
            """
            When 2 items are enqueued, low first, peek returns the second.
            """
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
            """
            When 2 items are enqueued, high first, peek returns the first.
            """
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
            """
            Interleaved operations behave properly as a max priority queue.
            """
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
            Interleaved peeks align with proper max priority queue order
            dequeuing.
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

        @parameterized.expand([
            ('distinct 5',
             ['e', 'd', 'c', 'a', 'b'],
             ['e', 'd', 'c', 'b', 'a']),
            ('distinct 12',
             [5, 6, 1, 10, 2, 9, 3, 8, 4, 7, 12, 11],
             [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
            ('some dupes',
             ['foo', 'bar', 'bar', 'baz', 'foo', 'bar'],
             ['foo', 'foo', 'baz', 'bar', 'bar', 'bar']),
            ('all dupes', [3, 3, 3], [3, 3, 3]),
        ])
        def test_enqueues_then_dequeues_descending_order(self, _label,
                                                         in_items,
                                                         expected_out_items):
            """Items dequeue in reverse-sorted order, no matter how many."""
            # Ensure error (not mere failure) if the test is itself wrong.
            if expected_out_items != sorted(in_items, reverse=True):
                raise Exception('bad test: expected should reverse input')

            pq = self.queue_type()

            for item in in_items:
                pq.enqueue(item)

            out_items = []
            while pq:
                out_items.append(pq.dequeue())

            self.assertListEqual(out_items, expected_out_items)

        def test_ordering_can_be_weak_Patient(self):
            """
            Priority queue elements do not have to be totally ordered.

            It is sufficient that order comparison is a weak ordering on all
            elements. This is a partial ordering where "is neither less than
            nor greater than" is transitive: if neither A < B nor B < A, and
            neither B < C nor C < B, then neither A < C nor C < A.

            In a weak ordering, elements clump together by incomparability. If
            X1, X2, ..., Xm can appear in any order, and Y1, Y1, ..., Yn can
            appear in any order, but some Xi < Yj, then weak ordering
            guarantees that every Xi is less than every Yj. That makes it so
            algorithms that make use of ordering and permit indistinguishable
            elements, such as comparison sorts, either already work with any
            weak ordering, or can be made to work without much redesign.

            Storing Patient instances in a priority queue may illuminate why
            this is important to support. In contrast, some partial orderings,
            like "<" on sets, offer even fewer guarantees than weak orderings,
            and most comparison-based algorithms can't feasibly support them.

            Even though this page is about C++, not Python, it may be helpful:

                https://en.cppreference.com/w/cpp/concepts/strict_weak_order
            """
            in1 = compare.Patient('AB', 1040)
            in2 = compare.Patient('CD', 1890)
            in3 = compare.Patient('EF', 1040)
            in4 = compare.Patient('GH', 1890)

            pq = self.queue_type()
            pq.enqueue(in1)
            pq.enqueue(in2)
            pq.enqueue(in3)
            pq.enqueue(in4)

            with self.subTest(expected_priority=1890):
                out1 = pq.dequeue()
                out2 = pq.dequeue()
                self.assertSetEqual({out1, out2}, {in2, in4})

            with self.subTest(expected_priority=1040):
                out1 = pq.dequeue()
                out2 = pq.dequeue()
                self.assertSetEqual({out1, out2}, {in1, in3})

        def test_ordering_can_be_weak_WeakDiamond(self):
            """
            Priority queue elements do not have to be totally ordered
            (alternative).

            See the test_ordering_can_be_weak_Patient docstring (above) for an
            explanation of weak ordering.

            Various ways of failing to support arbitrary weak orderings will
            succeed on some inputs and fail on others. Having this other test
            somewhat increases the likelihood that bugs will cause failures.
            """
            pq = self.queue_type()
            pq.enqueue(compare.WeakDiamond.NORTH)
            pq.enqueue(compare.WeakDiamond.EAST)
            pq.enqueue(compare.WeakDiamond.SOUTH)
            pq.enqueue(compare.WeakDiamond.WEST)

            with self.subTest('NORTH is considered highest'):
                out = pq.dequeue()
                self.assertEqual(out, compare.WeakDiamond.NORTH)

            with self.subTest('EAST and WEST are considered medial'):
                expected = {compare.WeakDiamond.EAST, compare.WeakDiamond.WEST}
                out1 = pq.dequeue()
                out2 = pq.dequeue()
                self.assertSetEqual({out1, out2}, expected)

            with self.subTest('SOUTH is considered lowest'):
                out = pq.dequeue()
                self.assertEqual(out, compare.WeakDiamond.SOUTH)


class TestQueue(_Bases.TestAbstract,
                _Bases.TestSignatures):
    """Tests for Queue class."""

    @property
    def queue_type(self):
        return queues.Queue


class TestFifoQueue(_Bases.TestAbstract,
                    _Bases.TestSignatures,
                    _Bases.TestSubclasses):
    """Tests for FifoQueue class."""

    @property
    def queue_type(self):
        return queues.FifoQueue


class TestLifoQueue(_Bases.TestAbstract,
                    _Bases.TestSignatures,
                    _Bases.TestSubclasses):
    """Tests for LifoQueue class."""

    @property
    def queue_type(self):
        return queues.LifoQueue


class TestPriorityQueue(_Bases.TestAbstract,
                        _Bases.TestSignatures,
                        _Bases.TestSubclasses):
    """Tests for PriorityQueue class."""

    @property
    def queue_type(self):
        return queues.PriorityQueue


class TestDequeFifoQueue(_Bases.TestSignatures,
                         _Bases.TestSubclasses,
                         _Bases.TestConcrete,
                         _Bases.TestFifos):
    """Tests for DequeFifoQueue class."""

    @property
    def queue_type(self):
        return queues.DequeFifoQueue


class TestAltDequeFifoQueue(_Bases.TestSignatures,
                            _Bases.TestSubclasses,
                            _Bases.TestConcrete,
                            _Bases.TestFifos):
    """Tests for AltDequeFifoQueue class."""

    @property
    def queue_type(self):
        return queues.AltDequeFifoQueue


class TestSlowFifoQueue(_Bases.TestSignatures,
                        _Bases.TestSubclasses,
                        _Bases.TestConcrete,
                        _Bases.TestFifos):
    """Tests for SlowFifoQueue class."""

    @property
    def queue_type(self):
        return queues.SlowFifoQueue


class TestBiStackFifoQueue(_Bases.TestSignatures,
                           _Bases.TestSubclasses,
                           _Bases.TestConcrete,
                           _Bases.TestFifos):
    """Tests for BiStackFifoQueue class."""

    @property
    def queue_type(self):
        return queues.BiStackFifoQueue


class TestSinglyLinkedListFifoQueue(_Bases.TestSignatures,
                                    _Bases.TestSubclasses,
                                    _Bases.TestConcrete,
                                    _Bases.TestFifos):
    """Tests for SinglyLinkedListFifoQueue class."""

    @property
    def queue_type(self):
        return queues.SinglyLinkedListFifoQueue


class TestListLifoQueue(_Bases.TestSignatures,
                        _Bases.TestSubclasses,
                        _Bases.TestConcrete,
                        _Bases.TestLifos):
    """Tests for ListLifoQueue class."""

    @property
    def queue_type(self):
        return queues.ListLifoQueue


class TestDequeLifoQueue(_Bases.TestSignatures,
                         _Bases.TestSubclasses,
                         _Bases.TestConcrete,
                         _Bases.TestLifos):
    """Tests for DequeLifoQueue class."""

    @property
    def queue_type(self):
        return queues.DequeLifoQueue


class TestAltDequeLifoQueue(_Bases.TestSignatures,
                            _Bases.TestSubclasses,
                            _Bases.TestConcrete,
                            _Bases.TestLifos):
    """Tests for AltDequeLifoQueue class."""

    @property
    def queue_type(self):
        return queues.AltDequeLifoQueue


class TestSinglyLinkedListLifoQueue(_Bases.TestSignatures,
                                    _Bases.TestSubclasses,
                                    _Bases.TestConcrete,
                                    _Bases.TestLifos):
    """Tests for SinglyLinkedListLifoQueue class."""

    @property
    def queue_type(self):
        return queues.SinglyLinkedListLifoQueue


class TestFastEnqueueMaxPriorityQueue(_Bases.TestSignatures,
                                      _Bases.TestSubclasses,
                                      _Bases.TestConcrete,
                                      _Bases.TestPriorityQueues):
    """Tests for FastEnqueueMaxPriorityQueue class."""

    @property
    def queue_type(self):
        return queues.FastEnqueueMaxPriorityQueue


class TestFastDequeueMaxPriorityQueue(_Bases.TestSignatures,
                                      _Bases.TestSubclasses,
                                      _Bases.TestConcrete,
                                      _Bases.TestPriorityQueues):
    """Tests for FastDequeueMaxPriorityQueue class."""

    @property
    def queue_type(self):
        return queues.FastDequeueMaxPriorityQueue


if __name__ == '__main__':
    unittest.main()
