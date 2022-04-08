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

    __slots__ = ()

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

    __slots__ = ()

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


# FIXME: Add the rest of the tests.
