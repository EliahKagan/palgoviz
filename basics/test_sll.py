#!/usr/bin/env python

"""Tests for sll.py."""

import unittest

from parameterized import parameterized

import sll


class TestNode(unittest.TestCase):
    """Tests for the sll.Node class."""

    def test_cannot_construct_with_zero_args(self):
        with self.assertRaises(TypeError):
            sll.Node()

    def test_can_construct_with_one_arg(self):
        head = sll.Node('foo')
        self.assertIsInstance(head, sll.Node)

    def test_constructing_with_one_arg_has_value(self):
        head = sll.Node('foo')
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_one_arg_has_no_next_node(self):
        head = sll.Node('foo')
        self.assertIsNone(head.next_node)

    def test_cannot_construct_with_second_arg_not_of_node_type(self):
        """
        The next_node (i.e., second) argument must be an instance of sll.Node.

        Since we are doing hash consing, the effects of allowing a next_node of
        the wrong type are dire: the wrong behavior is both unintuitive and
        global. So it is important to check the type of next_node, even if
        runtime type-checking is not otherwise called for.
        """
        with self.assertRaises(TypeError):
            sll.Node('foo', object())

    def test_can_construct_with_two_args_second_none(self):
        head = sll.Node('foo', None)
        self.assertIsInstance(head, sll.Node)

    def test_constructing_with_two_args_second_none_has_value(self):
        head = sll.Node('foo', None)
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_two_args_second_none_has_no_next_node(self):
        head = sll.Node('foo', None)
        self.assertIsNone(head.next_node)

    def test_can_construct_with_two_args_second_node(self):
        head = sll.Node('foo', sll.Node('bar'))
        self.assertIsInstance(head, sll.Node)

    def test_constructing_with_two_args_second_node_has_value(self):
        head = sll.Node('foo', sll.Node('bar'))
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_two_args_second_node_has_it_as_next_node(self):
        next_node = sll.Node('bar')
        head = sll.Node('foo', next_node)
        self.assertIs(head.next_node, next_node)

    def test_value_attribute_is_read_only(self):
        """The value attribute cannot be written."""
        head = sll.Node('foo')
        with self.assertRaises(AttributeError):
            head.value = 'bar'

    def test_value_attribute_cannot_be_deleted(self):
        head = sll.Node('foo')
        with self.assertRaises(AttributeError):
            del head.value

    def test_next_node_attribute_is_read_only_if_none(self):
        """The next_node attribute cannot be written."""
        head = sll.Node('foo')
        with self.assertRaises(AttributeError):
            head.next_node = sll.Node('baz')

    def test_next_node_attribute_is_read_only_if_not_none(self):
        """The next_node attribute cannot be written."""
        head = sll.Node('foo', sll.Node('bar'))
        with self.assertRaises(AttributeError):
            head.next_node = sll.Node('baz')

    def test_next_node_attribute_cannot_be_deleted_if_none(self):
        head = sll.Node('foo')
        with self.assertRaises(AttributeError):
            del head.next_node

    def test_next_node_attribute_cannot_be_deleted_if_not_none(self):
        head = sll.Node('foo', sll.Node('bar'))
        with self.assertRaises(AttributeError):
            del head.next_node

    def test_new_attributes_cannot_be_created(self):
        head = sll.Node('foo')
        with self.assertRaises(AttributeError):
            head.new_attribute_created_pursuant_to_my_whims = 'oof'

    def test_no_instance_dictionary(self):
        """
        Instances should have no __dict__, for a low memory footprint.

        This is a separate requirement from the requirement that new attributes
        cannot be created. Often __slots__ are used as a way to achieve that
        without the complexity of overriding __setattr__ and modifying the code
        to accommodate its overridden logic. But sometimes our primary goal
        really is to use less memory (or, occasionally, to access attributes
        faster even aside from the speed benefits of lower memory usage). Node
        classes in linked data structures are a case where this is desirable,
        since, in many uses, a very large number of nodes may be created.
        """
        head = sll.Node('foo')
        with self.assertRaises(AttributeError):
            head.__dict__

    def test_repr_shows_no_next_node_if_none(self):
        head = sll.Node('foo')
        self.assertEqual(repr(head), "Node('foo')")

    def test_repr_shows_sll_recursively(self):
        expected = "Node('a', Node('b', Node('c', Node('d'))))"
        head = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        self.assertEqual(repr(head), expected)

    def test_nodes_holding_same_type_value_no_next_are_equal(self):
        lhs = sll.Node('foo')
        rhs = sll.Node('foo')
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_same_type_value_no_next_are_identical(self):
        lhs = sll.Node('foo')
        rhs = sll.Node('foo')
        self.assertIs(lhs, rhs)

    def test_nodes_holding_same_type_value_next_are_equal(self):
        lhs = sll.Node('foo', sll.Node('bar'))
        rhs = sll.Node('foo', sll.Node('bar'))
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_same_type_value_next_are_identical(self):
        lhs = sll.Node('foo', sll.Node('bar'))
        rhs = sll.Node('foo', sll.Node('bar'))
        self.assertIs(lhs, rhs)

    def test_nodes_heading_same_type_value_chain_are_equal(self):
        lhs = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        rhs = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        self.assertEqual(lhs, rhs)

    def test_nodes_heading_same_type_value_chain_are_identical(self):
        lhs = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        rhs = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        self.assertIs(lhs, rhs)

    def test_nodes_heading_different_values_no_next_are_not_equal(self):
        lhs = sll.Node('foo')
        rhs = sll.Node('bar')
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_different_values_no_next_are_not_identical(self):
        lhs = sll.Node('foo')
        rhs = sll.Node('bar')
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_different_values_same_next_are_not_equal(self):
        lhs = sll.Node('foo', sll.Node('baz'))
        rhs = sll.Node('bar', sll.Node('baz'))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_different_values_same_next_are_not_identical(self):
        lhs = sll.Node('foo', sll.Node('baz'))
        rhs = sll.Node('bar', sll.Node('baz'))
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_same_values_different_next_are_not_equal(self):
        lhs = sll.Node('foo', sll.Node('bar'))
        rhs = sll.Node('foo', sll.Node('baz'))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_same_values_different_next_are_not_identical(self):
        lhs = sll.Node('foo', sll.Node('bar'))
        rhs = sll.Node('foo', sll.Node('baz'))
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_different_length_chains_are_not_equal(self):
        shorter = sll.Node('foo')
        longer = sll.Node('foo', sll.Node('bar'))
        with self.subTest(lhs='shorter', rhs='longer'):
            self.assertNotEqual(shorter, longer)
        with self.subTest(lhs='longer', rhs='shorter'):
            self.assertNotEqual(longer, shorter)

    def test_nodes_heading_different_length_chains_are_not_identical(self):
        shorter = sll.Node('foo')
        longer = sll.Node('foo', sll.Node('bar'))
        with self.subTest(lhs='shorter', rhs='longer'):
            self.assertIsNot(shorter, longer)
        with self.subTest(lhs='longer', rhs='shorter'):
            self.assertIsNot(longer, shorter)

    @parameterized.expand([
        ('one', 1),
        ('zero', 0),
        ('obj', object()),
        ('none', None),
    ])
    def test_is_truthy(self, _name, value):
        head = sll.Node(value)
        self.assertTrue(head)

    @parameterized.expand(['__eq__', '__ne__', '__hash__'])
    def test_type_uses_reference_equality_comparison(self, name):
        expected = getattr(object, name)
        actual = getattr(sll.Node, name)
        self.assertIs(actual, expected)


if __name__ == '__main__':
    unittest.main()
