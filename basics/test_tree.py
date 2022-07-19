"""Tests for tree.py."""

from abc import ABC, abstractmethod
import functools
import inspect
import unittest

from parameterized import parameterized_class

import tree


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


def _wraps_unannotated(func):
    """
    Decorator factory like @functools.wraps, but doesn't copy __annotations__.

    As currently used in this module, this makes no difference, since I'm not
    using type annotations. I use this to avoid wrongly communicating that it
    would be correct (or make sense) to copy __annotations__ when it would not.
    """
    assigned = ('__module__', '__name__', '__qualname__', '__doc__')
    return functools.wraps(func, assigned=assigned)


def _example(func):
    """
    Convert a function taking a node-type argument to a _Maker-style method.

    This is used for _Maker, _BstMaker, and _AlmostBstMaker instance methods.
    """
    @_wraps_unannotated(func)
    def wrapper(self):
        return func(self.node_type)

    return wrapper


class _MakerBase:
    """Shared base class for _Maker, _BstMaker, and _AlmostBstMaker."""

    __slots__ = ('_node_type',)

    def __init__(self, node_type):
        """Create a maker that builds trees using the given node type."""
        self._node_type = node_type

    def __repr__(self):
        """Largely code-like representation suitable for debugging."""
        return f'{type(self).__name__}({self._node_type.__qualname__})'

    @property
    def node_type(self):
        """The type used to construct nodes in trees being built."""
        return self._node_type


class _TrivialMaker(_MakerBase):
    """Shared base class for _Maker and _BstMaker, but not _AlmostBstMaker."""

    __slots__ = ()

    @_example
    def empty(_t):
        """A "tree" with no nodes."""
        return None

    @_example
    def singleton(t):
        """A tree with only one node."""
        return t(1)


class _Maker(_TrivialMaker):
    """Factory for examples of small binary trees for use in testing."""

    __slots__ = ()

    @_example
    def left_only(t):
        """A tree with a root and left child."""
        return t(1, t(2), None)

    @_example
    def right_only(t):
        """A tree with a root and right child."""
        return t(2, None, t(1))  # Deliberately not a BST. See _BstMaker.

    @_example
    def tiny(t):
        """A 3-node tree of minimal height."""
        return t(1, t(2), t(3))

    @_example
    def small(t):
        """A 7-node tree of minimal height."""
        return t(1, t(2, t(4), t(5)), t(3, t(6), t(7)))

    @_example
    def small_no_left_left(t):
        """A 6-node balanced tree, with the 1st bottom-level position empty."""
        return t(1, t(2, None, t(4)), t(3, t(5), t(6)))

    @_example
    def small_no_left_right(t):
        """A 6-node balanced tree, with the 2nd bottom-level position empty."""
        return t(1, t(2, t(4), None), t(3, t(5), t(6)))

    @_example
    def small_no_right_left(t):
        """A 6-node balanced tree, with the 3rd bottom-level position empty."""
        return t(1, t(2, t(4), t(5)), t(3, None, t(6)))

    @_example
    def small_no_right_right(t):
        """A 6-node balanced tree, with the 4th bottom-level position empty."""
        return t(1, t(2, t(4), t(5)), t(3, t(6), None))

    # FIXME: Write the rest of the methods.


class _BstMaker(_TrivialMaker):
    """Factory for examples of small binary search trees for use in testing."""

    __slots__ = ()

    # FIXME: Write the methods.


class _AlmostBstMaker(_MakerBase):
    """Factory of small not-quite-BST binary trees, for testing is_bst*."""

    __slots__ = ()

    # FIXME: Write the methods.


_parameterize_class_by_node_type = parameterized_class(('name', 'node_type'), [
    (tree.Node.__name__, tree.Node),
    (tree.FrozenNode.__name__, tree.FrozenNode),
])


@_parameterize_class_by_node_type
class TestPreorder(unittest.TestCase):
    """Tests for the preorder function."""

    # FIXME: Write the tests. Use _Maker and _BstMaker example trees.
