"""Tests for queues.py."""

import inspect
import unittest

from parameterized import parameterized_class

import queues


def _unannotated_argspec(func):
    """Get the full argspec of a callable object, but without annotations."""
    return inspect.getfullargspec(func)[:6]


@parameterized_class(('name', 'queue_type'), [
    ('Queue', queues.Queue),
    ('FifoQueue', queues.FifoQueue),
    ('LifoQueue', queues.LifoQueue),
])
class TestAbstractQueues(unittest.TestCase):
    """Tests for abstract queue types."""

    def test_is_abstract(self):
        self.assertTrue(inspect.isabstract(self.queue_type))

    def test_abstract_methods_are_bool_len_enqueue_dequeue(self):
        expected = {'__bool__', '__len__', 'enqueue', 'dequeue'}
        actual = self.queue_type.__abstractmethods__
        self.assertSetEqual(actual, expected)


@parameterized_class(('name', 'queue_type'), [
    ('Queue', queues.Queue),
    ('FifoQueue', queues.FifoQueue),
    ('LifoQueue', queues.LifoQueue),
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
    ('ListLifoQueue', queues.ListLifoQueue),
    ('DequeLifoQueue', queues.DequeLifoQueue),
    ('AltDequeLifoQueue', queues.AltDequeLifoQueue),
])
class TestQueueMethodSignatures(unittest.TestCase):
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


@parameterized_class(('name', 'queue_type'), [
    ('FifoQueue', queues.FifoQueue),
    ('LifoQueue', queues.LifoQueue),
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
    ('ListLifoQueue', queues.ListLifoQueue),
    ('DequeLifoQueue', queues.DequeLifoQueue),
    ('AltDequeLifoQueue', queues.AltDequeLifoQueue),
])
class TestCreateMethods(unittest.TestCase):
    """Tests that create() class-methods work as expected."""

    def test_create_creates_instance_of_class_it_is_called_on(self):
        """
        Calling create on a queue class creates an instance of that class.

        It need not be a direct instance. When the class it is called on is
        abstract, it will not be a direct instance. (Currently the abstract
        queue classes with create() methods are FifoQueue and LifoQueue.)
        """
        queue = self.queue_type.create()
        self.assertIsInstance(queue, self.queue_type)

    def test_queue_returned_by_create_is_empty(self):
        """create() methods return queues that are falsy, thus empty."""
        queue = self.queue_type.create()
        self.assertFalse(queue)


@parameterized_class(('name', 'factory'), [
    ('DequeFifoQueue', queues.DequeFifoQueue),
    ('AltDequeFifoQueue', queues.AltDequeFifoQueue),
    ('SlowFifoQueue', queues.SlowFifoQueue),
    ('BiStackFifoQueue', queues.BiStackFifoQueue),
])
class TestFifos(unittest.TestCase):
    """Tests for concrete FIFO queue ("queue") behavior."""

    # FIXME: Write these tests.


# FIXME: Add the rest of the test classes.
