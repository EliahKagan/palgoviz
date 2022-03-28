"""Tests for queues.py."""

import inspect
import unittest

from queues import Queue


def _unannotated_argspec(func):
    """Get the full argspec of a callable object, but without annotations."""
    return inspect.getfullargspec(func)[:6]


class TestQueue(unittest.TestCase):
    """Tests for the Queue abstract class."""

    __slots__ = ()

    def test_is_abstract(self):
        self.assertTrue(inspect.isabstract(Queue))

    def test_abstract_methods_are_bool_len_enqueue_dequeue(self):
        expected = {'__bool__', '__len__', 'enqueue', 'dequeue'}
        actual = Queue.__abstractmethods__
        self.assertSetEqual(actual, expected)

    def test_bool_method_has_data_model_recommended_signature(self):
        """The __bool__ method accepts no arguments (besides self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(Queue.__bool__)
        self.assertTupleEqual(actual, expected)

    def test_len_method_has_data_model_recommended_signature(self):
        """The __len__ method accepts no arguments (besides self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(Queue.__len__)
        self.assertTupleEqual(actual, expected)

    def test_enqueue_method_has_item_parameter_and_no_extras(self):
        """The enqueue method accepts only an item argument (and self)."""
        expected = (['self', 'item'], None, None, None, [], None)
        actual = _unannotated_argspec(Queue.enqueue)
        self.assertTupleEqual(actual, expected)

    def test_dequeue_method_has_no_extra_parameters(self):
        """The dequeue method accepts no arguments (except self)."""
        expected = (['self'], None, None, None, [], None)
        actual = _unannotated_argspec(Queue.dequeue)
        self.assertTupleEqual(actual, expected)
