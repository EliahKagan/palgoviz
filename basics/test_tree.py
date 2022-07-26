#!/usr/bin/env python

"""Tests for tree.py."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
import enum
import inspect
import itertools
import sys
import unittest

from parameterized import parameterized, parameterized_class

import enumerations
import tree
from tree.examples import almost_bst, basic, bst, trivial

_NODE_TYPES = (tree.Node, tree.FrozenNode)
"""The binary tree node types that most functions are to be tested with."""


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


# TODO: Consider giving _Spy a more specific name and moving it to a module of
# testing helpers (perhaps testing.py), even if no other test modules need it.
# If other test modules would benefit from it, then definitely do that.
class _Spy:
    """
    Context manager to patch/unpatch a callable in a module to count calls.

    This is used for temporarily patching Node and FrozenNode to ensure
    functions that make nodes call them the correct number of times. A fixture
    mixin is not a good way to cause tests in this module do that, as patching
    is needed for some parts of test cases, yet must not happen in other parts.

    >>> with _Spy(tree.Node) as spy:
    ...     basic.small(tree.Node)
    Node(1, Node(2, Node(4), Node(5)), Node(3, Node(6), Node(7)))
    >>> tree.Node
    <class 'tree.Node'>
    >>> spy.call_count
    7
    """

    __slots__ = ('_module', '_wrapped', '_call_count')

    def __init__(self, cls):
        """Create a new _Spy. Find the target, but don't patch it yet."""
        self._module = sys.modules[cls.__module__]
        if getattr(self._module, cls.__name__) is not cls:
            raise ValueError("node class in module doesn't match")
        self._wrapped = cls
        self._call_count = 0

    def __repr__(self):
        """Code-like representation of this _Spy context manager object."""
        return f'{type(self).__name__}({self._wrapped.__qualname__})'

    def __enter__(self):
        """Patch the target callable to count calls."""
        if getattr(self._module, self._wrapped.__name__) is not self._wrapped:
            raise ValueError('node class in module no longer matches')
        setattr(self._module, self._wrapped.__name__, self._call_wrapped)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Unpatch the target callable. This stops counting calls to it."""
        del exc_type, exc_value, traceback
        setattr(self._module, self._wrapped.__name__, self._wrapped)

    @property
    def call_count(self):
        """How many times the target callable has been called while patched."""
        return self._call_count

    def _call_wrapped(self, *args, **kwargs):
        """Increment the call count and call the original target callable."""
        self._call_count += 1
        return self._wrapped(*args, **kwargs)


def _static_callable(f):
    """Wrap a callable f, if needed/correct for use in @parameterized_class."""
    return staticmethod(f) if inspect.isfunction(f) else f


def _parameterize_class_by_implementation(*implementations):
    """Parameterize a test class by the function/class of code under test."""
    return parameterized_class(('name', 'implementation'), [
        (implementation.__name__, _static_callable(implementation))
        for implementation in implementations
    ])


def _parameterize_by(*iterables, row_filter=None):
    """Parameterize a test by a named Cartesian product of iterables."""
    rows = itertools.product(*iterables)
    if row_filter is not None:
        rows = (row for row in rows if row_filter(*row))
    named = [('_'.join(elem.__name__ for elem in row), *row) for row in rows]
    return parameterized.expand(named)


_parameterize_by_node_type = _parameterize_by(_NODE_TYPES)
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


@_parameterize_class_by_implementation(
    tree.copy,
    tree.copy_iterative,
)
class TestCopy(unittest.TestCase):
    """
    Tests for functions that copy the structure and values of a binary tree.

    Copying and structural equality comparison are closely related. The tests
    in this class test only copying. If the copying functions are correctly
    implemented but the structural equality comparison functions are buggy or
    unimplemented, these tests should all still pass.
    """

    @_parameterize_by_node_type
    def test_empty_returns_none(self, _name, node_type):
        original = trivial.empty(tree.Node)

        if original is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(original)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_nonempty_returns_node(self, _name, node_type):
        """Copied trees are made of Node, regardless of the input node type."""
        root = basic.small(node_type)
        result = self.implementation(root)
        self.assertIsInstance(result, tree.Node)

    @_parameterize_by_node_type
    def test_empty_creates_no_nodes(self, _name, node_type):
        original = trivial.empty(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 0)

    @_parameterize_by_node_type
    def test_singleton_reprs_match(self, _name, node_type):
        expected = trivial.singleton(tree.Node)
        original = trivial.singleton(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_singleton_creates_node(self, _name, node_type):
        original = trivial.singleton(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by_node_type
    def test_left_only_reprs_match(self, _name, node_type):
        expected = basic.left_only(tree.Node)
        original = basic.left_only(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_left_only_creates_nodes(self, _name, node_type):
        original = basic.left_only(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 2)

    @_parameterize_by_node_type
    def test_left_only_bst_reprs_match(self, _name, node_type):
        expected = bst.left_only(tree.Node)
        original = bst.left_only(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_left_only_bst_creates_nodes(self, _name, node_type):
        original = bst.left_only(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 2)

    @_parameterize_by_node_type
    def test_right_only_reprs_match(self, _name, node_type):
        expected = basic.right_only(tree.Node)
        original = basic.right_only(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_right_only_creates_nodes(self, _name, node_type):
        original = basic.right_only(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 2)

    @_parameterize_by_node_type
    def test_right_only_bst_reprs_match(self, _name, node_type):
        expected = bst.right_only(tree.Node)
        original = bst.right_only(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_right_only_bst_creates_nodes(self, _name, node_type):
        original = bst.right_only(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 2)

    @_parameterize_by_node_type
    def test_tiny_reprs_match(self, _name, node_type):
        expected = basic.tiny(tree.Node)
        original = basic.tiny(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_tiny_creates_nodes(self, _name, node_type):
        original = basic.tiny(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 3)

    @_parameterize_by_node_type
    def test_tiny_bst_reprs_match(self, _name, node_type):
        expected = bst.tiny(tree.Node)
        original = bst.tiny(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_tiny_bst_creates_nodes(self, _name, node_type):
        original = bst.tiny(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 3)

    @_parameterize_by_node_type
    def test_small_reprs_match(self, _name, node_type):
        expected = basic.small(tree.Node)
        original = basic.small(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_creates_nodes(self, _name, node_type):
        original = basic.small(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 7)

    @_parameterize_by_node_type
    def test_small_bst_reprs_match(self, _name, node_type):
        expected = bst.small(tree.Node)
        original = bst.small(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_bst_creates_nodes(self, _name, node_type):
        original = bst.small(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 7)

    @_parameterize_by_node_type
    def test_small_no_left_left_reprs_match(self, _name, node_type):
        expected = basic.small_no_left_left(tree.Node)
        original = basic.small_no_left_left(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_left_left_creates_nodes(self, _name, node_type):
        original = basic.small_no_left_left(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_left_left_bst_reprs_match(self, _name, node_type):
        expected = bst.small_no_left_left(tree.Node)
        original = bst.small_no_left_left(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_left_left_bst_creates_nodes(self, _name, node_type):
        original = bst.small_no_left_left(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_left_right_reprs_match(self, _name, node_type):
        expected = basic.small_no_left_right(tree.Node)
        original = basic.small_no_left_right(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_left_right_creates_nodes(self, _name, node_type):
        original = basic.small_no_left_right(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_left_right_bst_reprs_match(self, _name, node_type):
        expected = bst.small_no_left_right(tree.Node)
        original = bst.small_no_left_right(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_left_right_bst_creates_nodes(self, _name, node_type):
        original = bst.small_no_left_right(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_right_left_reprs_match(self, _name, node_type):
        expected = basic.small_no_right_left(tree.Node)
        original = basic.small_no_right_left(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_right_left_creates_nodes(self, _name, node_type):
        original = basic.small_no_right_left(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_right_left_bst_reprs_match(self, _name, node_type):
        expected = bst.small_no_right_left(tree.Node)
        original = bst.small_no_right_left(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_right_left_bst_creates_nodes(self, _name, node_type):
        original = bst.small_no_right_left(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_right_right_reprs_match(self, _name, node_type):
        expected = basic.small_no_right_right(tree.Node)
        original = basic.small_no_right_right(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_right_right_creates_nodes(self, _name, node_type):
        original = basic.small_no_right_right(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_small_no_right_right_bst_reprs_match(self, _name, node_type):
        expected = bst.small_no_right_right(tree.Node)
        original = bst.small_no_right_right(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_small_no_right_right_bst_creates_nodes(self, _name, node_type):
        original = bst.small_no_right_right(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 6)

    @_parameterize_by_node_type
    def test_left_degenerate_reprs_match(self, _name, node_type):
        expected = basic.left_degenerate(tree.Node)
        original = basic.left_degenerate(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_left_degenerate_creates_nodes(self, _name, node_type):
        original = basic.left_degenerate(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_left_degenerate_bst_reprs_match(self, _name, node_type):
        expected = bst.left_degenerate(tree.Node)
        original = bst.left_degenerate(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_left_degenerate_bst_creates_nodes(self, _name, node_type):
        original = bst.left_degenerate(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_right_degenerate_reprs_match(self, _name, node_type):
        expected = basic.right_degenerate(tree.Node)
        original = basic.right_degenerate(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_right_degenerate_creates_nodes(self, _name, node_type):
        original = basic.right_degenerate(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_right_degenerate_bst_reprs_match(self, _name, node_type):
        expected = bst.right_degenerate(tree.Node)
        original = bst.right_degenerate(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_right_degenerate_bst_creates_nodes(self, _name, node_type):
        original = bst.right_degenerate(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_zigzag_degenerate_reprs_match(self, _name, node_type):
        expected = basic.zigzag_degenerate(tree.Node)
        original = basic.zigzag_degenerate(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_zigzag_degenerate_creates_nodes(self, _name, node_type):
        original = basic.zigzag_degenerate(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst_reprs_match(self, _name, node_type):
        expected = bst.zigzag_degenerate(tree.Node)
        original = bst.zigzag_degenerate(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_zigzag_degenerate_bst_creates_nodes(self, _name, node_type):
        original = bst.zigzag_degenerate(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_lefty_reprs_match(self, _name, node_type):
        expected = basic.lefty(tree.Node)
        original = basic.lefty(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_lefty_creates_nodes(self, _name, node_type):
        original = basic.lefty(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 9)

    @_parameterize_by_node_type
    def test_lefty_bst_reprs_match(self, _name, node_type):
        expected = bst.lefty(tree.Node)
        original = bst.lefty(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_lefty_bst_creates_nodes(self, _name, node_type):
        original = bst.lefty(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 9)

    @_parameterize_by_node_type
    def test_righty_reprs_match(self, _name, node_type):
        expected = basic.righty(tree.Node)
        original = basic.righty(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_righty_creates_nodes(self, _name, node_type):
        original = basic.righty(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 9)

    @_parameterize_by_node_type
    def test_righty_bst_reprs_match(self, _name, node_type):
        expected = bst.righty(tree.Node)
        original = bst.righty(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_righty_bst_creates_nodes(self, _name, node_type):
        original = bst.righty(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 9)

    @_parameterize_by_node_type
    def test_medium_reprs_match(self, _name, node_type):
        expected = basic.medium(tree.Node)
        original = basic.medium(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_medium_creates_nodes(self, _name, node_type):
        original = basic.medium(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 24)

    @_parameterize_by_node_type
    def test_medium_bst_reprs_match(self, _name, node_type):
        expected = bst.medium(tree.Node)
        original = bst.medium(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_medium_bst_creates_nodes(self, _name, node_type):
        original = bst.medium(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 24)

    @_parameterize_by_node_type
    def test_medium_redundant_reprs_match(self, _name, node_type):
        expected = basic.medium_redundant(tree.Node)
        original = basic.medium_redundant(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_medium_redundant_creates_nodes(self, _name, node_type):
        original = basic.medium_redundant(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 24)


@_parameterize_class_by_implementation(
    tree.structural_equal,
    tree.structural_equal_iterative,
)
class TestStructuralEqual(unittest.TestCase):
    """
    Tests for functions to check if binary trees match in structure and values.

    Copying and structural equality comparison are closely related. The tests
    in this class test only structural equality comparison. If the structural
    equality comparison functions are correctly implemented but the copying
    functions are buggy or unimplemented, these tests should all still pass.

    These tests include comparison of trees that have the same values and the
    same structure except with one node absent, as well as trees with the same
    structure but different values, trees that differ even more substantially,
    and trees that really are structurally equal to one another.
    """

    _FACTORIES = [
        trivial.empty,
        trivial.singleton,
        basic.left_only,
        bst.left_only,
        basic.right_only,
        bst.right_only,
        basic.tiny,
        bst.tiny,
        basic.small,
        bst.small,
        basic.small_no_left_left,
        bst.small_no_left_left,
        basic.small_no_left_right,
        bst.small_no_left_right,
        basic.small_no_right_left,
        bst.small_no_right_left,
        basic.small_no_right_right,
        bst.small_no_right_right,
        basic.left_degenerate,
        bst.left_degenerate,
        basic.right_degenerate,
        bst.right_degenerate,
        basic.zigzag_degenerate,
        bst.zigzag_degenerate,
        basic.lefty,
        bst.lefty,
        basic.righty,
        bst.righty,
        basic.medium,
        bst.medium,
        basic.medium_redundant,
    ]
    """Tree factories from example.trivial, example.basic, and example.bst."""

    @_parameterize_by(_FACTORIES, _NODE_TYPES, _NODE_TYPES)
    def test_equal(self, _name, factory, lhs_node_type, rhs_node_type):
        lhs = factory(lhs_node_type)
        rhs = factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertTrue(result)

    # FIXME: This adds 7440 tests. That's too many. They take too long to run.
    @_parameterize_by(_FACTORIES, _FACTORIES, _NODE_TYPES, _NODE_TYPES,
                      row_filter=lambda lf, rf, _lnt, _rnt: lf is not rf)
    def test_unequal(self, _name,
                     lhs_factory, rhs_factory, lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
