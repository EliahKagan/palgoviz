#!/usr/bin/env python

"""Tests for the simple code in simple.py."""

import unittest

from simple import MY_NONE, Widget, answer, is_sorted


class TestMyNone(unittest.TestCase):
    """The MY_NONE constant doesn't need any tests. Here's one anyway."""

    __slots__ = ()

    def test_my_none_is_none(self):
        self.assertIsNone(MY_NONE)


# TODO: Extract common code to a setUp method.
class TestWidget(unittest.TestCase):
    """Tests for the Widget class."""

    __slots__ = ()

    def test_size_attribute_has_size(self):
        widget = Widget('vast', 'mauve')
        self.assertEqual(widget.size, 'vast')

    def test_color_attribute_has_color(self):
        widget = Widget('vast', 'mauve')
        self.assertEqual(widget.color, 'mauve')

    def test_size_can_be_changed(self):
        widget = Widget('vast', 'mauve')
        widget.size = 'just barely visible'
        self.assertEqual(widget.size, 'just barely visible')

    def test_color_can_be_changed(self):
        widget = Widget('vast', 'mauve')  # Arrange.
        widget.color = 'royal purple'  # Act.
        self.assertEqual(widget.color, 'royal purple')  # Assert.

    def test_new_attributes_cannot_be_added(self):
        widget = Widget('vast', 'mauve')
        with self.assertRaises(AttributeError):
            widget.favorite_desert = 'Sahara'


class TestAnswer(unittest.TestCase):
    """Test the answer() function."""

    __slots__ = ()

    def test_the_answer_is_42(self):
        answer_to_the_question = answer()
        self.assertEqual(answer_to_the_question, 42)

    def test_the_answer_is_an_int(self):
        answer_to_the_question = answer()
        self.assertIsInstance(answer_to_the_question, int)


class TestIsSorted(unittest.TestCase):
    """Tests for the is_sorted function."""

    __slots__ = ()

    def test_empty_list_is_sorted(self):
        items = []
        self.assertTrue(is_sorted(items))

    def test_empty_generator_is_sorted(self):
        items = (x for x in ())
        self.assertTrue(is_sorted(items))

    def test_one_element_list_is_sorted(self):
        items = [76]
        self.assertTrue(is_sorted(items))

    def test_one_element_generator_is_sorted(self):
        items = (x for x in (76,))
        self.assertTrue(is_sorted(items))

    def test_ascending_two_element_list_is_sorted(self):
        items = ['a', 'b']
        self.assertTrue(is_sorted(items))

    def test_descending_two_element_list_is_not_sorted(self):
        items = ['b', 'a']
        self.assertFalse(is_sorted(items))

    def test_descending_two_element_generator_is_not_sorted(self):
        items = (x for x in (3, 2))
        self.assertFalse(is_sorted(items))

    def test_ascending_two_element_generator_is_sorted(self):
        items = (ch for ch in 'ab')
        self.assertTrue(is_sorted(items))

    def test_equal_two_element_list_is_sorted(self):
        items = ['a', 'a']
        self.assertTrue(is_sorted(items))

    def test_equal_two_element_generator_is_sorted(self):
        items = (ch for ch in 'aa')
        self.assertTrue(is_sorted(items))

    def test_sorted_short_but_nontrivial_list_is_sorted(self):
        items = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
        self.assertTrue(is_sorted(items))

    def test_unsorted_short_but_nontrivial_is_unsorted(self):
        items = ['bar', 'eggs', 'foo', 'ham', 'foobar', 'quux', 'baz', 'spam']
        self.assertFalse(is_sorted(items))


if __name__ == '__main__':
    unittest.main()
