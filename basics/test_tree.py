#!/usr/bin/env python

"""Tests for tree.py."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
import enum
import inspect
import unittest

from parameterized import parameterized, parameterized_class

import enumerations
import tree
from tree.examples import almost_bst, basic, bst, trivial


class _TestNodeBase(ABC, unittest.TestCase):
    """Base class providing shared tests for node classes."""

    @property
    @abstractmethod
    def node_type(self):
        """The node class being tested."""
        raise NotImplementedError

    @property
    def name(self):
        """The name of the node type. (Override if node_type isn't a class.)"""
        return self.node_type.__name__

    def test_cannot_construct_with_no_args(self):
        with self.assertRaises(TypeError):
            self.node_type()

    def test_one_positional_arg_is_element(self):
        node = self.node_type('hello')
        self.assertEqual(node.element, 'hello')

    def test_one_arg_constructs_with_no_left_child(self):
        node = self.node_type('hello')
        self.assertIsNone(node.left)

    def test_one_arg_constructs_with_no_right_child(self):
        node = self.node_type('hello')
        self.assertIsNone(node.right)

    def test_three_positional_args_first_is_element(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left, right)
        self.assertEqual(root.element, 'P')

    def test_three_positional_args_second_is_left_child(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left, right)
        self.assertIs(root.left, left)

    def test_three_positional_args_third_is_right_child(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left, right)
        self.assertIs(root.right, right)

    def test_positional_arg_is_element_with_left_keyword_arg(self):
        left = self.node_type('LC')
        root = self.node_type('P', left=left)
        self.assertEqual(root.element, 'P')

    def test_with_positional_arg_left_keyword_arg_is_left_child(self):
        left = self.node_type('LC')
        root = self.node_type('P', left=left)
        self.assertIs(root.left, left)

    def test_no_right_child_with_positional_and_left_keyword_arg(self):
        left = self.node_type('LC')
        root = self.node_type('P', left=left)
        self.assertIsNone(root.right)

    def test_positional_arg_is_element_with_right_keyword_arg(self):
        right = self.node_type('RC')
        root = self.node_type('P', right=right)
        self.assertEqual(root.element, 'P')

    def test_with_positional_arg_right_keyword_arg_is_right_child(self):
        right = self.node_type('RC')
        root = self.node_type('P', right=right)
        self.assertIs(root.right, right)

    def test_no_left_child_with_positional_and_right_keyword_arg(self):
        right = self.node_type('RC')
        root = self.node_type('P', right=right)
        self.assertIsNone(root.left)

    def test_with_positional_and_both_keyword_args_positional_is_element(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left=left, right=right)
        self.assertEqual(root.element, 'P')

    def test_with_positional_and_both_keyword_args_left_is_left_child(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left=left, right=right)
        self.assertIs(root.left, left)

    def test_with_positional_and_both_keyword_args_right_is_right_child(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left=left, right=right)
        self.assertIs(root.right, right)

    def test_cannot_construct_without_element_arg(self):
        left = self.node_type('LC')
        right = self.node_type('RC')
        with self.assertRaises(TypeError):
            self.node_type(left=left, right=right)

    def test_repr_of_leaf_shows_just_element_arg(self):
        node = self.node_type('hello')
        self.assertEqual(repr(node), f"{self.name}('hello')")

    def test_repr_with_both_children_shows_three_positional_args(self):
        expected = f"{self.name}('P', {self.name}('LC'), {self.name}('RC'))"
        left = self.node_type('LC')
        right = self.node_type('RC')
        root = self.node_type('P', left=left, right=right)
        self.assertEqual(repr(root), expected)

    def test_repr_with_just_left_child_shows_three_positional_args(self):
        expected = f"{self.name}('P', {self.name}('LC'), None)"
        left = self.node_type('LC')
        root = self.node_type('P', left=left)
        self.assertEqual(repr(root), expected)

    def test_repr_with_just_right_child_shows_three_positional_args(self):
        expected = f"{self.name}('P', None, {self.name}('RC'))"
        right = self.node_type('RC')
        root = self.node_type('P', right=right)
        self.assertEqual(repr(root), expected)

    def test_different_instances_are_not_equal(self):
        """This represents a node, not subtree. Reference equality applies."""
        lhs = self.node_type('A')
        rhs = self.node_type('B')
        if lhs is rhs:
            raise Exception("separate nodes are identical, can't test ==")
        self.assertNotEqual(lhs, rhs)

    def test_cannot_reassign_element(self):
        node = self.node_type('hello')
        with self.assertRaises(AttributeError):
            node.element = 'goodbye'

    def test_cannot_create_attributes_by_assignment(self):
        node = self.node_type('hello')
        with self.assertRaises(AttributeError):
            node.center = 'CC'

    def test_no_instance_dictionary(self):
        """To save memory, nodes shouldn't usually have __dict__."""
        node = self.node_type('hello')
        with self.assertRaises(AttributeError):
            node.__dict__

    def test_element_documented_as_element(self):
        doc = inspect.getdoc(self.node_type.element)
        self.assertEqual(doc, 'The element held in this node.')

    def test_left_documented_as_left_child(self):
        doc = inspect.getdoc(self.node_type.left)
        self.assertEqual(doc, 'The left child.')

    def test_right_documented_as_right_child(self):
        doc = inspect.getdoc(self.node_type.right)
        self.assertEqual(doc, 'The right child.')


class TestNode(_TestNodeBase):
    """Tests for the Node class."""

    @property
    def node_type(self):
        return tree.Node

    def test_can_reassign_left_child(self):
        root = tree.Node('P')
        left = tree.Node('LC')
        root.left = left
        self.assertIs(root.left, left)

    def test_can_reassign_left_child_none(self):
        left = tree.Node('LC')
        root = tree.Node('P', left=left)
        root.left = None
        self.assertIsNone(root.left)

    def test_can_reassign_right_child(self):
        root = tree.Node('P')
        right = tree.Node('RC')
        root.right = right
        self.assertIs(root.right, right)

    def test_can_reassign_right_child_none(self):
        right = tree.Node('RC')
        root = tree.Node('P', right=right)
        root.right = None
        self.assertIsNone(root.right)

    def test_left_is_not_property(self):
        """It can be reassigned and isn't validated. Not worth a property."""
        self.assertNotIsInstance(tree.Node.left, property)

    def test_right_is_not_property(self):
        """It can be reassigned and isn't validated. Not worth a property."""
        self.assertNotIsInstance(tree.Node.right, property)


class TestFrozenNode(_TestNodeBase):
    """Tests for the FrozenNode class."""

    @property
    def node_type(self):
        return tree.FrozenNode

    def test_cannot_reassign_left_child(self):
        root = tree.FrozenNode('P')
        left = tree.FrozenNode('LC')
        with self.assertRaises(AttributeError):
            root.left = left

    def test_cannot_reassign_left_child_none(self):
        left = tree.FrozenNode('LC')
        root = tree.FrozenNode('P', left=left)
        with self.assertRaises(AttributeError):
            root.left = None

    def test_cannot_reassign_right_child(self):
        root = tree.FrozenNode('P')
        right = tree.FrozenNode('RC')
        with self.assertRaises(AttributeError):
            root.right = right

    def test_cannot_reassign_right_child_none(self):
        right = tree.FrozenNode('RC')
        root = tree.FrozenNode('P', right=right)
        with self.assertRaises(AttributeError):
            root.right = None


del _TestNodeBase


def _static_callable(f):
    """Wrap a callable f, if needed/correct for use in @parameterized_class."""
    return staticmethod(f) if inspect.isfunction(f) else f


def _parameterize_class_by_implementation(*implementations):
    """Parameterize a test class by the function/class of code under test."""
    return parameterized_class(('name', 'implementation'), [
        (implementation.__name__, _static_callable(implementation))
        for implementation in implementations
    ])


_parameterize_by_node_type = parameterized.expand([
    (node_type.__name__, node_type)
    for node_type in (tree.Node, tree.FrozenNode)
])
"""Parameterize a test method by what class is used to instantiate nodes."""


@_parameterize_class_by_implementation(
    tree.preorder,
    tree.preorder_iterative,
    tree.green.preorder_via_general_dfs,
)
class TestPreorder(unittest.TestCase):
    """Tests for callables returning preorder traversal iterators."""

    @_parameterize_by_node_type
    def test_returns_iterator(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, Iterator)

    def test_empty(self):
        """The result of preorder traversing an empty "tree" is empty."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root)

        with self.assertRaises(StopIteration):
            next(result)

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1])

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3])

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1, 3])

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 5, 3, 6, 7])

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 1, 3, 6, 5, 7])

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 3, 5, 6])

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 3, 6, 5, 7])

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 3, 5, 6])

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 1, 6, 5, 7])

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 5, 3, 6])

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 1, 3, 6, 7])

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 5, 3, 6])

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 1, 3, 6, 5])

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 5, 2, 4, 3])

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 6, 8, 9, 7, 5, 3])

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [8, 6, 4, 2, 1, 3, 5, 7, 9])

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1, 4, 3, 6, 5, 8, 7, 9])

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        expected = [1, 2, 4, 8, 16, 17, 9, 18, 5, 10, 19, 20, 11, 21,
                    3, 6, 12, 13, 7, 14, 1, 2, 15, 3]
        root = basic.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        expected = [11, 4, 2, 1, 1, 2, 3, 3, 8, 6, 5, 7, 10, 9,
                    15, 13, 12, 14, 19, 17, 16, 18, 20, 21]
        root = bst.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        expected = [1, 2, 7, 14, 1, 2, 15, 3, 5, 6, 12, 13, 11, 21,
                    3, 6, 12, 13, 7, 14, 1, 2, 15, 3]
        root = basic.medium_redundant(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)


@_parameterize_class_by_implementation(
    tree.inorder,
    tree.green.inorder_via_general_dfs,
)
class TestInorder(unittest.TestCase):
    """Tests for callables returning inorder traversal iterators."""

    @_parameterize_by_node_type
    def test_returns_iterator(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, Iterator)

    def test_empty(self):
        """The result of inorder traversing an empty "tree" is empty."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root)

        with self.assertRaises(StopIteration):
            next(result)

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1])

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1, 3])

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3])

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 5, 1, 6, 3, 7])

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7])

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 4, 1, 5, 3, 6])

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 3, 4, 5, 6, 7])

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 1, 5, 3, 6])

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 4, 5, 6, 7])

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 5, 1, 3, 6])

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 6, 7])

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 5, 1, 6, 3])

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6])

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 5, 4, 2])

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [8, 6, 9, 4, 7, 2, 5, 1, 3])

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1, 4, 3, 6, 5, 8, 7, 9])

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        expected = [16, 8, 17, 4, 9, 18, 2, 19, 10, 20, 5, 21, 11,
                    1, 12, 6, 13, 3, 1, 14, 2, 7, 15, 3]
        root = basic.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        expected = [1, 1, 2, 2, 3, 3, 4, 5, 6, 7, 8, 9, 10,
                    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        root = bst.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        expected = [1, 14, 2, 7, 15, 3, 2, 12, 6, 13, 5, 21, 11,
                    1, 12, 6, 13, 3, 1, 14, 2, 7, 15, 3]
        root = basic.medium_redundant(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)


@_parameterize_class_by_implementation(
    tree.postorder,
    tree.green.postorder_via_general_dfs,
)
class TestPostorder(unittest.TestCase):
    """Tests for callables returning postorder traversal iterators."""

    @_parameterize_by_node_type
    def test_returns_iterator(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, Iterator)

    def test_empty(self):
        """The result of postorder traversing an empty "tree" is empty."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root)

        with self.assertRaises(StopIteration):
            next(result)

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1])

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 3, 1])

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 2])

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 5, 2, 6, 7, 3, 1])

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 2, 5, 7, 6, 4])

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 5, 6, 3, 1])

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [3, 2, 5, 7, 6, 4])

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 5, 6, 3, 1])

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 5, 7, 6, 4])

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 5, 2, 6, 3, 1])

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 2, 7, 6, 4])

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 5, 2, 6, 3, 1])

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 2, 5, 6, 4])

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [3, 4, 2, 5, 1])

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [8, 9, 6, 7, 4, 5, 2, 3, 1])

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 2, 5, 4, 7, 6, 9, 8])

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 4, 6, 8, 9, 7, 5, 3, 1])

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 5, 7, 9, 8, 6, 4, 2])

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        expected = [16, 17, 8, 18, 9, 4, 19, 20, 10, 21, 11, 5, 2,
                    12, 13, 6, 1, 2, 14, 3, 15, 7, 3, 1]
        root = basic.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        expected = [1, 2, 1, 3, 3, 2, 5, 7, 6, 9, 10, 8, 4,
                    12, 14, 13, 16, 18, 17, 21, 20, 19, 15, 11]
        root = bst.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        expected = [1, 2, 14, 3, 15, 7, 12, 13, 6, 21, 11, 5, 2,
                    12, 13, 6, 1, 2, 14, 3, 15, 7, 3, 1]
        root = basic.medium_redundant(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)


@enum.unique
class _Visit(enumerations.CodeReprEnum):
    """Whether an action ("visitation") is preorder, inorder, or postorder."""
    PRE = enum.auto()
    IN = enum.auto()
    POST = enum.auto()


def _run_general_dfs(root):
    """Run tree.general_dfs and return a sequence of logged actions."""
    visits = []

    tree.general_dfs(root,
                     pre_fn=lambda value: visits.append((_Visit.PRE, value)),
                     in_fn=lambda value: visits.append((_Visit.IN, value)),
                     post_fn=lambda value: visits.append((_Visit.POST, value)))

    return visits


class TestGeneralDfs(unittest.TestCase):
    """
    Tests of nontrivial uses of general_dfs.

    Functions in the green submodule perform pure preorder, inorder, and
    postorder traversals by delegating to general_dfs. Those indirect uses,
    some of which would most likely fail if general_dfs is implemented wrongly,
    are tested in TestPreorder, TestInorder, and TestPostorder, along with
    tests of the regular preorder, inorder, and postorder functions.

    This class tests more sophisticated usage that does not reduce to just one
    of preorder, inorder, or postorder traversal.
    """
    @_parameterize_by_node_type
    def test_returns_none(self, _name, node_type):
        """general_dfs should implicitly return None."""
        root = basic.small(node_type)
        actual_return = tree.general_dfs(root)
        self.assertIsNone(actual_return)

    def test_empty(self):
        """There are no nodes to visit in an empty "tree"."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        results = _run_general_dfs(root)
        self.assertListEqual(results, [])

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
        ])

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.POST, 2)
        ])

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.POST, 1)
        ])

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
        ])

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 2),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.IN, 3),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 6),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 6),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 6),
            (_Visit.POST, 4),
        ])

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 3),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 6),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 6),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 6),
            (_Visit.POST, 4),
        ])

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 3),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 6),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 6),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 6),
            (_Visit.POST, 4),
        ])

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 2),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 6),
            (_Visit.POST, 4),
        ])

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 2),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 6),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.POST, 4),
        ])

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 3),
            (_Visit.PRE, 4),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 5),
            (_Visit.PRE, 4),
            (_Visit.PRE, 3),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
        ])

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.POST, 2),
            (_Visit.POST, 3),
            (_Visit.POST, 4),
            (_Visit.POST, 5),
        ])

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 4),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.PRE, 4),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.POST, 3),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.PRE, 5),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.PRE, 4),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.POST, 2),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 4),
            (_Visit.PRE, 6),
            (_Visit.PRE, 8),
            (_Visit.IN, 8),
            (_Visit.POST, 8),
            (_Visit.IN, 6),
            (_Visit.PRE, 9),
            (_Visit.IN, 9),
            (_Visit.POST, 9),
            (_Visit.POST, 6),
            (_Visit.IN, 4),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 4),
            (_Visit.IN, 2),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 8),
            (_Visit.PRE, 6),
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.POST, 4),
            (_Visit.IN, 6),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 6),
            (_Visit.IN, 8),
            (_Visit.PRE, 9),
            (_Visit.IN, 9),
            (_Visit.POST, 9),
            (_Visit.POST, 8),
        ])

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 4),
            (_Visit.IN, 4),
            (_Visit.POST, 4),
            (_Visit.IN, 3),
            (_Visit.PRE, 5),
            (_Visit.PRE, 6),
            (_Visit.IN, 6),
            (_Visit.POST, 6),
            (_Visit.IN, 5),
            (_Visit.PRE, 7),
            (_Visit.PRE, 8),
            (_Visit.IN, 8),
            (_Visit.POST, 8),
            (_Visit.IN, 7),
            (_Visit.PRE, 9),
            (_Visit.IN, 9),
            (_Visit.POST, 9),
            (_Visit.POST, 7),
            (_Visit.POST, 5),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 4),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.IN, 4),
            (_Visit.PRE, 6),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 6),
            (_Visit.PRE, 8),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.IN, 8),
            (_Visit.PRE, 9),
            (_Visit.IN, 9),
            (_Visit.POST, 9),
            (_Visit.POST, 8),
            (_Visit.POST, 6),
            (_Visit.POST, 4),
            (_Visit.POST, 2),
        ])

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        root = basic.medium(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 4),
            (_Visit.PRE, 8),
            (_Visit.PRE, 16),
            (_Visit.IN, 16),
            (_Visit.POST, 16),
            (_Visit.IN, 8),
            (_Visit.PRE, 17),
            (_Visit.IN, 17),
            (_Visit.POST, 17),
            (_Visit.POST, 8),
            (_Visit.IN, 4),
            (_Visit.PRE, 9),
            (_Visit.IN, 9),
            (_Visit.PRE, 18),
            (_Visit.IN, 18),
            (_Visit.POST, 18),
            (_Visit.POST, 9),
            (_Visit.POST, 4),
            (_Visit.IN, 2),
            (_Visit.PRE, 5),
            (_Visit.PRE, 10),
            (_Visit.PRE, 19),
            (_Visit.IN, 19),
            (_Visit.POST, 19),
            (_Visit.IN, 10),
            (_Visit.PRE, 20),
            (_Visit.IN, 20),
            (_Visit.POST, 20),
            (_Visit.POST, 10),
            (_Visit.IN, 5),
            (_Visit.PRE, 11),
            (_Visit.PRE, 21),
            (_Visit.IN, 21),
            (_Visit.POST, 21),
            (_Visit.IN, 11),
            (_Visit.POST, 11),
            (_Visit.POST, 5),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 6),
            (_Visit.PRE, 12),
            (_Visit.IN, 12),
            (_Visit.POST, 12),
            (_Visit.IN, 6),
            (_Visit.PRE, 13),
            (_Visit.IN, 13),
            (_Visit.POST, 13),
            (_Visit.POST, 6),
            (_Visit.IN, 3),
            (_Visit.PRE, 7),
            (_Visit.PRE, 14),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 14),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.POST, 14),
            (_Visit.IN, 7),
            (_Visit.PRE, 15),
            (_Visit.IN, 15),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 15),
            (_Visit.POST, 7),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        root = bst.medium(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 11),
            (_Visit.PRE, 4),
            (_Visit.PRE, 2),
            (_Visit.PRE, 1),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 1),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.POST, 1),
            (_Visit.IN, 2),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 2),
            (_Visit.IN, 4),
            (_Visit.PRE, 8),
            (_Visit.PRE, 6),
            (_Visit.PRE, 5),
            (_Visit.IN, 5),
            (_Visit.POST, 5),
            (_Visit.IN, 6),
            (_Visit.PRE, 7),
            (_Visit.IN, 7),
            (_Visit.POST, 7),
            (_Visit.POST, 6),
            (_Visit.IN, 8),
            (_Visit.PRE, 10),
            (_Visit.PRE, 9),
            (_Visit.IN, 9),
            (_Visit.POST, 9),
            (_Visit.IN, 10),
            (_Visit.POST, 10),
            (_Visit.POST, 8),
            (_Visit.POST, 4),
            (_Visit.IN, 11),
            (_Visit.PRE, 15),
            (_Visit.PRE, 13),
            (_Visit.PRE, 12),
            (_Visit.IN, 12),
            (_Visit.POST, 12),
            (_Visit.IN, 13),
            (_Visit.PRE, 14),
            (_Visit.IN, 14),
            (_Visit.POST, 14),
            (_Visit.POST, 13),
            (_Visit.IN, 15),
            (_Visit.PRE, 19),
            (_Visit.PRE, 17),
            (_Visit.PRE, 16),
            (_Visit.IN, 16),
            (_Visit.POST, 16),
            (_Visit.IN, 17),
            (_Visit.PRE, 18),
            (_Visit.IN, 18),
            (_Visit.POST, 18),
            (_Visit.POST, 17),
            (_Visit.IN, 19),
            (_Visit.PRE, 20),
            (_Visit.IN, 20),
            (_Visit.PRE, 21),
            (_Visit.IN, 21),
            (_Visit.POST, 21),
            (_Visit.POST, 20),
            (_Visit.POST, 19),
            (_Visit.POST, 15),
            (_Visit.POST, 11),
        ])

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        results = _run_general_dfs(root)
        self.assertListEqual(results, [
            (_Visit.PRE, 1),
            (_Visit.PRE, 2),
            (_Visit.PRE, 7),
            (_Visit.PRE, 14),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 14),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.POST, 14),
            (_Visit.IN, 7),
            (_Visit.PRE, 15),
            (_Visit.IN, 15),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 15),
            (_Visit.POST, 7),
            (_Visit.IN, 2),
            (_Visit.PRE, 5),
            (_Visit.PRE, 6),
            (_Visit.PRE, 12),
            (_Visit.IN, 12),
            (_Visit.POST, 12),
            (_Visit.IN, 6),
            (_Visit.PRE, 13),
            (_Visit.IN, 13),
            (_Visit.POST, 13),
            (_Visit.POST, 6),
            (_Visit.IN, 5),
            (_Visit.PRE, 11),
            (_Visit.PRE, 21),
            (_Visit.IN, 21),
            (_Visit.POST, 21),
            (_Visit.IN, 11),
            (_Visit.POST, 11),
            (_Visit.POST, 5),
            (_Visit.POST, 2),
            (_Visit.IN, 1),
            (_Visit.PRE, 3),
            (_Visit.PRE, 6),
            (_Visit.PRE, 12),
            (_Visit.IN, 12),
            (_Visit.POST, 12),
            (_Visit.IN, 6),
            (_Visit.PRE, 13),
            (_Visit.IN, 13),
            (_Visit.POST, 13),
            (_Visit.POST, 6),
            (_Visit.IN, 3),
            (_Visit.PRE, 7),
            (_Visit.PRE, 14),
            (_Visit.PRE, 1),
            (_Visit.IN, 1),
            (_Visit.POST, 1),
            (_Visit.IN, 14),
            (_Visit.PRE, 2),
            (_Visit.IN, 2),
            (_Visit.POST, 2),
            (_Visit.POST, 14),
            (_Visit.IN, 7),
            (_Visit.PRE, 15),
            (_Visit.IN, 15),
            (_Visit.PRE, 3),
            (_Visit.IN, 3),
            (_Visit.POST, 3),
            (_Visit.POST, 15),
            (_Visit.POST, 7),
            (_Visit.POST, 3),
            (_Visit.POST, 1),
        ])


@_parameterize_class_by_implementation(
    tree.levelorder,
    # NOTE: In the future we will have multiple level-order traversers to test.
)
class TestLevelOrder(unittest.TestCase):
    """Tests for callables returning level-order traversal iterators."""

    @_parameterize_by_node_type
    def test_returns_iterator(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, Iterator)

    def test_empty(self):
        """The result of level-order traversing an empty "tree" is empty."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root)

        with self.assertRaises(StopIteration):
            next(result)

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1])

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1])

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2])

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3])

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1, 3])

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7])

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 6, 1, 3, 5, 7])

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6])

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 6, 3, 5, 7])

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6])

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 6, 1, 5, 7])

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6])

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 6, 1, 3, 7])

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6])

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [4, 2, 6, 1, 3, 5])

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 5, 2, 4, 3])

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [8, 6, 9, 4, 7, 2, 5, 1, 3])

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [2, 1, 4, 3, 6, 5, 8, 7, 9])

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                    16, 17, 18, 19, 20, 21, 1, 2, 3]
        root = basic.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        expected = [11, 4, 15, 2, 8, 13, 19, 1, 3, 6, 10, 12, 14, 17, 20,
                    1, 2, 3, 5, 7, 9, 16, 18, 21]
        root = bst.medium(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        expected = [1, 2, 3, 7, 5, 6, 7, 14, 15, 6, 11, 12, 13, 14, 15,
                    1, 2, 3, 12, 13, 21, 1, 2, 3]
        root = basic.medium_redundant(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), expected)


@_parameterize_class_by_implementation(
    tree.size,
    tree.size_recursive,
    tree.size_iterative,
)
class TestSize(unittest.TestCase):
    """Tests for functions that count all nodes in a binary tree."""

    @_parameterize_by_node_type
    def test_returns_int(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, int)

    def test_empty(self):
        """The result of level-order traversing an empty "tree" is empty."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root)
        self.assertEqual(result, 0)

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 3)

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 3)

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 7)

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 7)

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 6)

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 9)

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 9)

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 9)

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 9)

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 24)

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 24)

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 24)


@_parameterize_class_by_implementation(
    tree.height,
    tree.height_iterative,
    tree.height_iterative_alt,
)
class TestHeight(unittest.TestCase):
    """Tests for functions that find the height of a binary tree."""

    @_parameterize_by_node_type
    def test_returns_int(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, int)

    def test_empty(self):
        """The result of level-order traversing an empty "tree" is empty."""
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root)
        self.assertEqual(result, -1)

    @_parameterize_by_node_type
    def test_singleton(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 0)

    @_parameterize_by_node_type
    def test_left_only(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_left_only_bst(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_right_only(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_right_only_bst(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_tiny(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_tiny_bst(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @_parameterize_by_node_type
    def test_small(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_bst(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_left_left(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_left_left_bst(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_left_right(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_left_right_bst(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_right_left(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_right_left_bst(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_right_right(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_small_no_right_right_bst(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 2)

    @_parameterize_by_node_type
    def test_left_degenerate(self, _name, node_type):
        root = basic.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_left_degenerate_bst(self, _name, node_type):
        root = bst.left_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_right_degenerate(self, _name, node_type):
        root = basic.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_right_degenerate_bst(self, _name, node_type):
        root = bst.right_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_zigzag_degenerate(self, _name, node_type):
        root = basic.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst(self, _name, node_type):
        root = bst.zigzag_degenerate(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_lefty(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_lefty_bst(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_righty(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_righty_bst(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_medium(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_medium_bst(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_medium_redundant(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)


if __name__ == '__main__':
    unittest.main()
