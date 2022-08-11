#!/usr/bin/env python

"""Tests for the tree module."""

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
from tree.examples import almost_bst, basic, bilateral, bst, mirror, trivial


def _zip_strict(*iterables):
    """Zip iterables, raising ValueError if any differ in length."""
    return zip(*iterables, strict=True)


_NODE_TYPES = (tree.Node, tree.FrozenNode)
"""The binary tree node types that most functions are to be tested with."""

_VERY_SMALL_TREE_FACTORIES = [
    trivial.empty,
    trivial.singleton,
    basic.left_only,
    bst.left_only,
    basic.right_only,
    bst.right_only,
    basic.tiny,
    bst.tiny,
]
"""Factories for very small trees."""

_SMALL_TREE_FACTORIES = [
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
]
"""Factories for small trees. This omits basic.small_str and bst.small_str."""

_TEXT_TREE_FACTORIES = [
    basic.small_str,
    bst.small_str,
]
"""Factories for small trees with string elements."""

_CHAIN_TREE_FACTORIES = [
    basic.left_chain,
    bst.left_chain,
    basic.right_chain,
    bst.right_chain,
    basic.zigzag_chain,
    bst.zigzag_chain,
]
"""Factories for degenerate trees: those that are single chains."""

_LEANING_TREE_FACTORIES = [
    basic.lefty,
    bst.lefty,
    basic.righty,
    bst.righty,
]
"""Factories for trees that are chains except opposite singleton branches."""

_MEDIUM_TREE_FACTORIES = [
    basic.medium,
    bst.medium,
    basic.medium_redundant,
]
"""Factories for medium-sized trees, same structure, different elements."""

_TREE_FACTORIES = [
    *_VERY_SMALL_TREE_FACTORIES,
    *_SMALL_TREE_FACTORIES,
    *_TEXT_TREE_FACTORIES,
    *_CHAIN_TREE_FACTORIES,
    *_LEANING_TREE_FACTORIES,
    *_MEDIUM_TREE_FACTORIES,
]
"""
All factories from example.trivial, example.basic, and example.bst.

These are all the general-purpose tree factories, but it does not include the
special-purpose ones. See the tree.examples package docstring and submodules.

This also does not automatically pick up new factories that may be added to the
trivial, basic, and bst submodules, because it is not clear, if that were to
happen, whether (or how) they ought to cause more unit tests to be generated.
"""

_BASIC_TREE_FACTORIES = [
    basic.left_only,
    basic.right_only,
    basic.tiny,
    basic.small,
    basic.small_str,
    basic.small_no_left_left,
    basic.small_no_left_right,
    basic.small_no_right_left,
    basic.small_no_right_right,
    basic.left_chain,
    basic.right_chain,
    basic.zigzag_chain,
    basic.lefty,
    basic.righty,
    basic.medium,
    basic.medium_redundant,
]
"""Factories from tree.example.basic."""

_MIRROR_TREE_FACTORIES = [
    mirror.left_only,
    mirror.right_only,
    mirror.tiny,
    mirror.small,
    mirror.small_str,
    mirror.small_no_left_left,
    mirror.small_no_left_right,
    mirror.small_no_right_left,
    mirror.small_no_right_right,
    mirror.left_chain,
    mirror.right_chain,
    mirror.zigzag_chain,
    mirror.lefty,
    mirror.righty,
    mirror.medium,
    mirror.medium_redundant,
]
"""Factories from tree.example.mirror. On names, see that module docstring."""

assert all(bas.__name__ == mir.__name__ for bas, mir
           in _zip_strict(_BASIC_TREE_FACTORIES, _MIRROR_TREE_FACTORIES))

_BST_TREE_FACTORIES = [
    bst.left_only,
    bst.right_only,
    bst.tiny,
    bst.small,
    bst.small_str,
    bst.small_no_left_left,
    bst.small_no_left_right,
    bst.small_no_right_left,
    bst.small_no_right_right,
    bst.left_chain,
    bst.right_chain,
    bst.zigzag_chain,
    bst.lefty,
    bst.righty,
    bst.medium,
]
"""Factories from example.bst."""

_ALMOST_BST_TREE_FACTORIES = [
    almost_bst.small,
    almost_bst.small_str,
    almost_bst.lefty,
    almost_bst.righty,
    almost_bst.medium,
]

_BILATERALLY_SYMMETRIC_TREE_FACTORIES = [
    bilateral.tiny,
    bilateral.small,
    bilateral.small_no_corners,
    bilateral.small_no_center,
    bilateral.medium_large,
    bilateral.medium_large_redundant,
]
"""Factories from tree.example.bilateral."""


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


def _get_name_no_fallback(thing):
    """Get the __name__ attribute."""
    return thing.__name__


def _get_name_with_fallback(thing):
    """Get the __name__ attribute, but fall back to str if not present."""
    try:
        return thing.__name__
    except AttributeError:
        return str(thing)


def _join_names(*arguments, indices=None, strict=True):
    """
    Join the __name__ attributes of each argument together by underscores.

    If strict=False, then for any argument without __name__, its str is used.

    This is for use in building names of parameterized test cases. The objects
    whose names are used are typically passed as arguments to a test method.
    (This is why they are called "arguments" here.)

    If indices is None, then all arguments' names are joined. Otherwise,
    indices must be an iterable of indices of arguments whose names are to be
    used, and all other arguments do not contribute to the joined string. The
    order in which indices are given does not matter.
    """
    get_name = _get_name_no_fallback if strict else _get_name_with_fallback

    if indices is None:
        return '_'.join(get_name(arg) for arg in arguments)

    index_set = set(indices)

    return '_'.join(get_name(arg) for index, arg in enumerate(arguments)
                    if index in index_set)


def _static_callable(f):
    """Wrap a callable f, if needed/correct for use in @parameterized_class."""
    return staticmethod(f) if inspect.isfunction(f) else f


def _parameterize_class_by(combiner=itertools.product, **groups):
    """
    Parameterize a test class by combining iterables and naming the results.

    The iterables' elements are assumed to be callable.

    By default, the Cartesian product of the iterables is taken, by passing
    each iterable (that is, each keyword-argument value _parameterize_class_by
    receives) to itertools.product. To combine them in a different way, pass a
    different callable as the combiner argument. The combiner must accept each
    iterable as a separate positional argument and return an iterator that
    yields tuples of elements. For each such tuple, its elements will be used
    together to synthesize a test class.

    NOTE: When calling _parameterize_class_by with a custom combiner, you must
    ensure the tuples it yields preserve the order of fields. The kth field in
    each yielded element will be assigned to a class attribute named after the
    kth keyword-argument key. Examples of combiners that satisfy this are
    itertools.product (the default) and zip.
    """
    if 'name' in groups:
        raise ValueError("cannot name a group 'name'")

    rows = combiner(*groups.values())
    named = [(_join_names(*row), *map(_static_callable, row)) for row in rows]
    return parameterized_class(('name', *groups), named)


def _parameterize_class_by_implementation(*implementations):
    """Parameterize a test class by a single function or class under test."""
    return _parameterize_class_by(implementation=implementations)


# TODO: This is undesirably complex. Maybe overhaul parameterization helpers.
def _parameterize_by(*iterables,
                     combiner=itertools.product,
                     row_filter=None,
                     name_indices=None,
                     strict_names=True):
    """
    Parameterize a test method by combining iterables and naming the results.

    By default, the Cartesian product of the iterables is taken, by passing
    each iterable (that is, each positional argument _parameterize_by receives)
    to itertools.product. To combine them in a different way, pass a different
    callable as the combiner keyword-only argument. The combiner must accept
    each iterable as a separate positional argument and return an iterator that
    yields tuples of elements. For each such tuple, its elements will be passed
    together to a test-case method, after a name argument generated from them.
    That will happen when the tests are collected into test suites and run.

    If row_filter is None, all rows are used. Otherwise row_filter is called on
    each row, by passing the row's elements as separate arguments, to decide if
    the row is to be included.

    If name_indices is None, then all elements of each row are used to name the
    test based on that row. Otherwise name_indices is an iterable of indices of
    elements whose names are included in the test name. The order of indices in
    name_indices does not matter. Usually name_indices should be kept as None,
    but it can be useful if some elements always have the same name as others
    in the same row, or if some elements lack useful names.

    If strict_names is False, str(arg) is used as a fallback when arg.__name__
    does not exist, for arguments whose names are used. Otherwise the absence
    of __name__ attributes on arguments whose names are used is a hard error.
    """
    rows = combiner(*iterables)
    if row_filter is not None:
        rows = (row for row in rows if row_filter(*row))
    named = [(_join_names(*row, indices=name_indices, strict=strict_names), *row)
             for row in rows]
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 3, 5, 4, 2])

    @_parameterize_by_node_type
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
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
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
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
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
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
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
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
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
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
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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
    # NOTE: We'll eventually have multiple level-order traversers to test.
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [5, 4, 3, 2, 1])

    @_parameterize_by_node_type
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root)
        self.assertListEqual(list(result), [1, 2, 3, 4, 5])

    @_parameterize_by_node_type
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 5)

    @_parameterize_by_node_type
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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
    def test_left_chain(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_left_chain_bst(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_right_chain(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_right_chain_bst(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_zigzag_chain(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root)
        self.assertEqual(result, 4)

    @_parameterize_by_node_type
    def test_zigzag_chain_bst(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
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

    def test_empty_returns_none(self):
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
    def test_left_chain_reprs_match(self, _name, node_type):
        expected = basic.left_chain(tree.Node)
        original = basic.left_chain(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_left_chain_creates_nodes(self, _name, node_type):
        original = basic.left_chain(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_left_chain_bst_reprs_match(self, _name, node_type):
        expected = bst.left_chain(tree.Node)
        original = bst.left_chain(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_left_chain_bst_creates_nodes(self, _name, node_type):
        original = bst.left_chain(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_right_chain_reprs_match(self, _name, node_type):
        expected = basic.right_chain(tree.Node)
        original = basic.right_chain(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_right_chain_creates_nodes(self, _name, node_type):
        original = basic.right_chain(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_right_chain_bst_reprs_match(self, _name, node_type):
        expected = bst.right_chain(tree.Node)
        original = bst.right_chain(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_right_chain_bst_creates_nodes(self, _name, node_type):
        original = bst.right_chain(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_zigzag_chain_reprs_match(self, _name, node_type):
        expected = basic.zigzag_chain(tree.Node)
        original = basic.zigzag_chain(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_zigzag_chain_creates_nodes(self, _name, node_type):
        original = basic.zigzag_chain(node_type)
        with _Spy(tree.Node) as spy:
            self.implementation(original)
        self.assertEqual(spy.call_count, 5)

    @_parameterize_by_node_type
    def test_zigzag_chain_bst_reprs_match(self, _name, node_type):
        expected = bst.zigzag_chain(tree.Node)
        original = bst.zigzag_chain(node_type)
        actual = self.implementation(original)
        self.assertEqual(repr(actual), repr(expected))

    @_parameterize_by_node_type
    def test_zigzag_chain_bst_creates_nodes(self, _name, node_type):
        original = bst.zigzag_chain(node_type)
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

    @_parameterize_by(_TREE_FACTORIES, _NODE_TYPES, _NODE_TYPES)
    def test_equal(self, _name, factory, lhs_node_type, rhs_node_type):
        lhs = factory(lhs_node_type)
        rhs = factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertTrue(result)

    def _parameterize_unequal_test(tree_factory_group):
        """
        Parameterize a test method on tree factory pairs and node types.

        This is for parameterizing tests that verify that trees differing by
        structure or corresponding elements are found to be structurally
        unequal. As such, tree factories are not paired with themselves, which
        would generate structurally equal trees.

        The test_unequal_* methods use this function. Unlike with test_equal,
        there are several test_unequal* methods in order to break the factories
        up into groups, to avoid generating too many test cases. Each group
        produces quadratically many tests; the sum of the squares of the group
        sizes is much smaller than the square of the sum of the group sizes.
        """
        def factories_are_distinct(lhs_factory, rhs_factory, *_):
            return lhs_factory is not rhs_factory

        return _parameterize_by(tree_factory_group,
                                tree_factory_group,
                                _NODE_TYPES,
                                _NODE_TYPES,
                                row_filter=factories_are_distinct)

    @_parameterize_unequal_test(_VERY_SMALL_TREE_FACTORIES)
    def test_unequal_very_small(self, _name, lhs_factory, rhs_factory,
                                lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)

    @_parameterize_unequal_test(_SMALL_TREE_FACTORIES)
    def test_unequal_small(self, _name, lhs_factory, rhs_factory,
                           lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)

    @_parameterize_unequal_test(_TEXT_TREE_FACTORIES)
    def test_unequal_text(self, _name, lhs_factory, rhs_factory,
                          lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)

    @_parameterize_unequal_test(_CHAIN_TREE_FACTORIES)
    def test_unequal_chain(self, _name, lhs_factory, rhs_factory,
                           lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)

    @_parameterize_unequal_test(_LEANING_TREE_FACTORIES)
    def test_unequal_leaning(self, _name, lhs_factory, rhs_factory,
                             lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)

    @_parameterize_unequal_test(_MEDIUM_TREE_FACTORIES)
    def test_unequal_medium(self, _name, lhs_factory, rhs_factory,
                            lhs_node_type, rhs_node_type):
        lhs = lhs_factory(lhs_node_type)
        rhs = rhs_factory(rhs_node_type)
        result = self.implementation(lhs, rhs)
        self.assertFalse(result)


@_parameterize_class_by(
    copy_impl=[tree.copy, tree.copy_iterative],
    eq_impl=[tree.structural_equal, tree.structural_equal_iterative],
)
class TestCopyStructuralEqual(unittest.TestCase):
    """
    Tests for the expected relationship of copying to structural equality.

    These tests test the binary tree copying functions together with the binary
    tree structural equality comparison functions. They test that, when a tree
    is copied, the copy is structurally equal to the original.

    Bugs in either or both will most likely cause some of these tests to fail,
    but it is possible for all to pass if the bugs are complementary. (But then
    tests in at least one of TestCopy and TestStructuralEqual should fail.)
    """

    @_parameterize_by(_TREE_FACTORIES, _NODE_TYPES)
    def test_copy_equals_original(self, _name, factory, node_type):
        original = factory(node_type)
        copy = self.copy_impl(original)
        result = self.eq_impl(copy, original)
        self.assertTrue(result)

    @_parameterize_by(_TREE_FACTORIES, _NODE_TYPES)
    def test_original_equals_copy(self, _name, factory, node_type):
        original = factory(node_type)
        copy = self.copy_impl(original)
        result = self.eq_impl(original, copy)
        self.assertTrue(result)


# TODO: Give this a more general name. Put it up by the other parameterizers.
def _parameterize_reflect_test(in_factories, out_factories):
    """
    Parameterize a test method by factory pairs produced by zipping.

    This is used in TestReflectInPlace and TestReflectInPlaceStructuralEqual.

    Only the name of the first factory is used, since the names should be the
    same. Also, if they were not the same, the first factory supplies the tree
    that is actually being reflected, while the second supplies the expected
    tree to compare against, so the first would be sufficient.
    """
    return _parameterize_by(in_factories, out_factories,
                            combiner=_zip_strict, name_indices=(0,))


@_parameterize_class_by_implementation(
    tree.reflect_in_place,
    tree.reflect_in_place_iterative,
)
class TestReflectInPlace(unittest.TestCase):
    """
    Tests for functions that turn a binary tree into its mirror image.

    These tests do not rely on structural_equality/structural_equal_iterative.
    """

    def test_returns_none(self):
        """None should be implicitly returned."""
        root = basic.small(tree.Node)
        result = self.implementation(root)
        self.assertIsNone(result)

    @_parameterize_by(_BILATERALLY_SYMMETRIC_TREE_FACTORIES)
    def test_bilaterally_symmetric_reflects_to_same(self, _name, factory):
        expected = factory(tree.Node)
        root = factory(tree.Node)
        if repr(root) != repr(expected):
            raise Exception("wrongly doesn't match expected before reflection")
        self.implementation(root)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_reflect_test(_BASIC_TREE_FACTORIES, _MIRROR_TREE_FACTORIES)
    def test_basic_reflects_to_mirror(self, _name, in_factory, out_factory):
        expected = out_factory(tree.Node)
        root = in_factory(tree.Node)
        if repr(root) == repr(expected):
            raise Exception('wrongly matches expected before reflection')
        self.implementation(root)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_reflect_test(_MIRROR_TREE_FACTORIES, _BASIC_TREE_FACTORIES)
    def test_mirror_reflects_to_basic(self, _name, in_factory, out_factory):
        expected = out_factory(tree.Node)
        root = in_factory(tree.Node)
        if repr(root) == repr(expected):
            raise Exception('wrongly matches expected before reflection')
        self.implementation(root)
        self.assertEqual(repr(root), repr(expected))


@_parameterize_class_by(
    reflect_impl=[tree.reflect_in_place, tree.reflect_in_place_iterative],
    eq_impl=[tree.structural_equal, tree.structural_equal_iterative],
)
class TestReflectInPlaceStructuralEqual(unittest.TestCase):
    """
    More tests for functions that turn a binary tree into its mirror image.

    Compared to the tests in TestReflectInPlace, which use repr, these test for
    structural equality, so they are likely to catch bugs in the structural
    equality functions, but also may fail to catch bugs in in-place reflection
    functions if there happen to be complementary structural equality bugs.
    """

    @_parameterize_by(_BILATERALLY_SYMMETRIC_TREE_FACTORIES)
    def test_bilateral_symmetry_preserves_equality_lhs(self, _name, factory):
        expected = factory(tree.Node)
        root = factory(tree.Node)
        if not self.eq_impl(root, expected):
            raise Exception("wrongly doesn't match expected before reflection")
        self.reflect_impl(root)
        result = self.eq_impl(root, expected)
        self.assertTrue(result)

    @_parameterize_by(_BILATERALLY_SYMMETRIC_TREE_FACTORIES)
    def test_bilateral_symmetry_preserves_equality_rhs(self, _name, factory):
        expected = factory(tree.Node)
        root = factory(tree.Node)
        if not self.eq_impl(expected, root):
            raise Exception("wrongly doesn't match expected before reflection")
        self.reflect_impl(root)
        result = self.eq_impl(expected, root)
        self.assertTrue(result)

    @_parameterize_reflect_test(_BASIC_TREE_FACTORIES, _MIRROR_TREE_FACTORIES)
    def test_reflected_basic_equals_mirror(self, _name,
                                           in_factory, out_factory):
        expected = out_factory(tree.Node)
        root = in_factory(tree.Node)
        if self.eq_impl(root, expected):
            raise Exception('wrongly matches expected before reflection')
        self.reflect_impl(root)
        result = self.eq_impl(root, expected)
        self.assertTrue(result)

    @_parameterize_reflect_test(_BASIC_TREE_FACTORIES, _MIRROR_TREE_FACTORIES)
    def test_mirror_equals_reflected_basic(self, _name,
                                           in_factory, out_factory):
        expected = out_factory(tree.Node)
        root = in_factory(tree.Node)
        if self.eq_impl(expected, root):
            raise Exception('wrongly matches expected before reflection')
        self.reflect_impl(root)
        result = self.eq_impl(expected, root)
        self.assertTrue(result)

    @_parameterize_reflect_test(_MIRROR_TREE_FACTORIES, _BASIC_TREE_FACTORIES)
    def test_reflected_mirror_equals_basic(self, _name,
                                           in_factory, out_factory):
        expected = out_factory(tree.Node)
        root = in_factory(tree.Node)
        if self.eq_impl(root, expected):
            raise Exception('wrongly matches expected before reflection')
        self.reflect_impl(root)
        result = self.eq_impl(root, expected)
        self.assertTrue(result)

    @_parameterize_reflect_test(_MIRROR_TREE_FACTORIES, _BASIC_TREE_FACTORIES)
    def test_basic_equals_reflected_mirror(self, _name,
                                           in_factory, out_factory):
        expected = out_factory(tree.Node)
        root = in_factory(tree.Node)
        if self.eq_impl(expected, root):
            raise Exception('wrongly matches expected before reflection')
        self.reflect_impl(root)
        result = self.eq_impl(expected, root)
        self.assertTrue(result)


@_parameterize_class_by_implementation(
    tree.is_own_reflection,
    tree.is_own_reflection_iterative,
)
class TestIsOwnReflection(unittest.TestCase):
    """Tests for functions that check if a tree is its own reflection."""

    @_parameterize_by([trivial.empty, trivial.singleton], _NODE_TYPES)
    def test_trivial(self, _name, factory, node_type):
        """
        Binary trees without multiple nodes are their own reflections.

        This tests trees that are trivially bilaterally symmetric because they
        contain fewer than 2 nodes.
        """
        root = factory(node_type)
        result = self.implementation(root)
        self.assertTrue(result)

    @_parameterize_by(_BILATERALLY_SYMMETRIC_TREE_FACTORIES, _NODE_TYPES)
    def test_bilaterally_symmetric(self, _name, factory, node_type):
        """
        Bilaterally symmetric binary trees are their own reflections.

        This tests trees that are nontrivially bilaterally symmetric: they have
        more than 2 nodes, so their symmetry does not follow from their size.
        """
        root = factory(node_type)
        result = self.implementation(root)
        self.assertTrue(result)

    @_parameterize_by(_BASIC_TREE_FACTORIES, _NODE_TYPES)
    def test_bilaterally_asymmetric(self, _name, factory, node_type):
        """Bilaterally asymmetric binary trees aren't their own reflections."""
        root = factory(node_type)
        result = self.implementation(root)
        self.assertFalse(result)

    @_parameterize_by(_BST_TREE_FACTORIES, _NODE_TYPES)
    def test_bilaterally_asymmetric_bst(self, _name, factory, node_type):
        """Bilaterally asymmetric BSTs aren't their own reflections."""
        root = factory(node_type)
        result = self.implementation(root)
        self.assertFalse(result)


@_parameterize_class_by_implementation(
    tree.linear_search,
    tree.linear_search_iterative,
    tree.linear_search_mindepth,
    tree.linear_search_mindepth_alt,
)
class TestLinearSearch(unittest.TestCase):
    """
    Tests for functions that sequentially search for a node by value.

    These are tests for all the binary tree linear search functions. Some of
    those functions have guarantees about what nodes they find when there is
    more than one possible match. This is covered in subsequent test classes.
    """

    def test_empty_returns_none(self):
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root, 42)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_singleton_returns_none_if_absent(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root, 42)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_singleton_returns_node_if_present(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_does_not_search_by_node_object_itself(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root, root)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_left_only_absent(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root, 3)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_left_only_at_root(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_left_only_at_child(self, _name, node_type):
        root = basic.left_only(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_right_only_absent(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root, 3)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_right_only_at_root(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_right_only_at_child(self, _name, node_type):
        root = basic.right_only(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_tiny_absent(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root, 0)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_tiny_at_root(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_tiny_at_left(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_tiny_at_right(self, _name, node_type):
        root = basic.tiny(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_absent(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 8)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_at_root(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_at_left(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_at_left_left(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_at_left_right(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_at_right(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_at_right_left(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_small_at_right_right(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.right.right)

    @_parameterize_by_node_type
    def test_small_no_left_left_absent(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root, 0)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_left_left_present(self, _name, node_type):
        root = basic.small_no_left_left(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_no_left_right_absent(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root, 7)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_left_right_present(self, _name, node_type):
        root = basic.small_no_left_right(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_no_right_left_absent(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root, 3.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_right_left_present(self, _name, node_type):
        root = basic.small_no_right_left(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right.right)

    @_parameterize_by_node_type
    def test_small_no_right_right_absent(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root, 5.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_right_right_present(self, _name, node_type):
        root = basic.small_no_right_right(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_left_chain_absent(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root, 6)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_left_chain_present(self, _name, node_type):
        root = basic.left_chain(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root.left.left.left)

    @_parameterize_by_node_type
    def test_right_chain_absent(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root, 0)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_right_chain_present(self, _name, node_type):
        root = basic.right_chain(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.right.right.right)

    @_parameterize_by_node_type
    def test_zigzag_chain_absent(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root, 3.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_zigzag_chain_present(self, _name, node_type):
        root = basic.zigzag_chain(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.right.left.right.left)

    @_parameterize_by_node_type
    def test_lefty_absent(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root, 10)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_lefty_present(self, _name, node_type):
        root = basic.lefty(node_type)
        result = self.implementation(root, 9)
        self.assertIs(result, root.left.left.left.right)

    @_parameterize_by_node_type
    def test_righty_absent(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root, 10)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_righty_present(self, _name, node_type):
        root = basic.righty(node_type)
        result = self.implementation(root, 8)
        self.assertIs(result, root.right.right.right.left)

    @_parameterize_by_node_type
    def test_medium_absent(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 12.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_medium_shallow(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_medium_deep(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 21)
        self.assertIs(result, root.left.right.right.left)

    @_parameterize_by_node_type
    def test_medium_duplicated(self, _name, node_type):
        root = basic.medium(node_type)
        expected = {root.left, root.right.right.left.right}
        result = self.implementation(root, 2)
        self.assertIn(result, expected)

    @_parameterize_by_node_type
    def test_medium_redundant_absent(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root, 0)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_medium_redundant_similar_heights(self, _name, node_type):
        """Should find one of possible matches that are at heights 3 and 4."""
        root = basic.medium_redundant(node_type)
        expected = {root.right.left.left, root.left.right.left.left}
        result = self.implementation(root, 12)
        self.assertIn(result, expected)

    @_parameterize_by_node_type
    def test_medium_redundant_dissimilar_heights(self, _name, node_type):
        """Should find one of possible matches that are at heights 1 and 4."""
        root = basic.medium_redundant(node_type)
        expected = {root.left.left.right.right, root.right}
        result = self.implementation(root, 3)
        self.assertIn(result, expected)


@_parameterize_class_by_implementation(
    tree.linear_search_mindepth,
    tree.linear_search_mindepth_alt,
)
class TestLinearSearchMinDepth(unittest.TestCase):
    """Tests that "mindepth" linear search functions find min-depth matches."""

    @_parameterize_by_node_type
    def test_medium_at_root(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_at_left(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_at_right(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_medium_mirror_at_root(self, _name, node_type):
        root = mirror.medium(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_mirror_at_left(self, _name, node_type):
        root = mirror.medium(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_mirror_at_right(self, _name, node_type):
        root = mirror.medium(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_medium_redundant_at_root(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_redundant_at_left(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_redundant_at_right(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_medium_redundant_at_right_left(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_root(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_left(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_right(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_left_right(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.left.right)


# TODO: If this pattern of class parameterization is used again, extract it to
#       its own parameterization decorator (up with the other parameterizers).
@parameterized_class([
    dict(name=_join_names(tree.linear_search,
                          tree.linear_search_iterative),
         main_impl=_static_callable(tree.linear_search),
         alt_impl=_static_callable(tree.linear_search_iterative)),
    dict(name=_join_names(tree.linear_search_mindepth,
                          tree.linear_search_mindepth_alt),
         main_impl=_static_callable(tree.linear_search_mindepth),
         alt_impl=_static_callable(tree.linear_search_mindepth_alt))
])
class TestLinearSearchConsistency(unittest.TestCase):
    """
    Test that pairs of alternative linear searchers find the same nodes.

    When there are zero or one possible matches, any implementation that is
    itself correct (irrespective of consistency with other code) automatically
    must return the same result (that match, or None). But when there are
    multiple solutions, we impose some restrictions on some implementations.

    This tests the restriction that linear_search and linear_search_iterative
    must always return the same results, and that linear_search_mindepth and
    linear_search_mindepth_alt must always return the same results.
    """

    @_parameterize_by_node_type
    def test_medium_at_root_or_bottom(self, _name, node_type):
        root = basic.medium(node_type)
        self.assertIs(self.main_impl(root, 1), self.alt_impl(root, 1))

    @_parameterize_by_node_type
    def test_medium_at_left_or_bottom(self, _name, node_type):
        root = basic.medium(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_medium_at_right_or_bottom(self, _name, node_type):
        root = basic.medium(node_type)
        self.assertIs(self.main_impl(root, 3), self.alt_impl(root, 3))

    @_parameterize_by_node_type
    def test_medium_mirror_at_root_or_bottom(self, _name, node_type):
        root = mirror.medium(node_type)
        self.assertIs(self.main_impl(root, 1), self.alt_impl(root, 1))

    @_parameterize_by_node_type
    def test_medium_mirror_at_left_or_bottom(self, _name, node_type):
        root = mirror.medium(node_type)
        self.assertIs(self.main_impl(root, 3), self.alt_impl(root, 3))

    @_parameterize_by_node_type
    def test_medium_mirror_at_right_or_bottom(self, _name, node_type):
        root = mirror.medium(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_medium_redundant_at_root_or_bottom(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 1), self.alt_impl(root, 1))

    @_parameterize_by_node_type
    def test_medium_redundant_at_left_or_bottom(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_medium_redundant_at_right_or_bottom(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 3), self.alt_impl(root, 3))

    @_parameterize_by_node_type
    def test_medium_redundant_at_height_2_or_3(self, _name, node_type):
        root = basic.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 6), self.alt_impl(root, 6))

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_root_or_bottom(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 1), self.alt_impl(root, 1))

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_left_or_bottom(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 3), self.alt_impl(root, 3))

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_right_or_bottom(self, _name,
                                                        node_type):
        root = mirror.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_medium_redundant_mirror_at_height_2_or_3(self, _name, node_type):
        root = mirror.medium_redundant(node_type)
        self.assertIs(self.main_impl(root, 6), self.alt_impl(root, 6))

    @_parameterize_by_node_type
    def test_bilateral_tiny(self, _name, node_type):
        root = bilateral.tiny(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_bilateral_small_middle(self, _name, node_type):
        root = bilateral.small(node_type)
        self.assertIs(self.main_impl(root, 9), self.alt_impl(root, 9))

    @_parameterize_by_node_type
    def test_bilateral_small_bottom_corners(self, _name, node_type):
        root = bilateral.small(node_type)
        self.assertIs(self.main_impl(root, 4), self.alt_impl(root, 4))

    @_parameterize_by_node_type
    def test_bilateral_small_bottom_center(self, _name, node_type):
        root = bilateral.small(node_type)
        self.assertIs(self.main_impl(root, 5), self.alt_impl(root, 5))

    @_parameterize_by_node_type
    def test_bilateral_small_no_corners_middle(self, _name, node_type):
        root = bilateral.small_no_corners(node_type)
        self.assertIs(self.main_impl(root, 9), self.alt_impl(root, 9))

    @_parameterize_by_node_type
    def test_bilateral_small_no_corners_bottom(self, _name, node_type):
        root = bilateral.small_no_corners(node_type)
        self.assertIs(self.main_impl(root, 5), self.alt_impl(root, 5))

    @_parameterize_by_node_type
    def test_bilateral_small_no_center_middle(self, _name, node_type):
        root = bilateral.small_no_center(node_type)
        self.assertIs(self.main_impl(root, 9), self.alt_impl(root, 9))

    @_parameterize_by_node_type
    def test_bilateral_small_no_center_bottom(self, _name, node_type):
        root = bilateral.small_no_center(node_type)
        self.assertIs(self.main_impl(root, 4), self.alt_impl(root, 4))

    @_parameterize_by_node_type
    def test_bilateral_medium_large_at_top_or_bottom(self, _name, node_type):
        root = bilateral.medium_large(node_type)
        self.assertIs(self.main_impl(root, 1), self.alt_impl(root, 1))

    @_parameterize_by_node_type
    def test_bilateral_medium_large_at_left_right_or_bottom(self, _name,
                                                            node_type):
        root = bilateral.medium_large(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_bilateral_medium_large_at_right_left_or_bottom(self, _name,
                                                            node_type):
        root = bilateral.medium_large(node_type)
        self.assertIs(self.main_impl(root, 3), self.alt_impl(root, 3))

    @_parameterize_by_node_type
    def test_bilateral_medium_large_redundant_at_top_or_bottom(self, _name,
                                                               node_type):
        root = bilateral.medium_large_redundant(node_type)
        self.assertIs(self.main_impl(root, 1), self.alt_impl(root, 1))

    @_parameterize_by_node_type
    def test_bilateral_medium_large_redundant_at_left_right_or_bottom(
            self, _name, node_type):
        root = bilateral.medium_large_redundant(node_type)
        self.assertIs(self.main_impl(root, 2), self.alt_impl(root, 2))

    @_parameterize_by_node_type
    def test_bilateral_medium_large_redundant_at_right_left_or_bottom(
            self, _name, node_type):
        root = bilateral.medium_large_redundant(node_type)
        self.assertIs(self.main_impl(root, 3), self.alt_impl(root, 3))


@_parameterize_class_by_implementation(
    tree.nearest_ancestor,
    # NOTE: We'll eventually have multiple nearest-ancestor functions to test.
)
class TestNearestAncestor(unittest.TestCase):
    """Tests for functions to find nodes and their lowest shared ancestor."""

    @_parameterize_by_node_type
    def test_small_itself(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 2, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_sibling(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 7, 6)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_first_cousin(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 5, 7)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_child(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 2, 4)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_parent(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 4, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_niece(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 3, 5)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_aunt(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 5, 3)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_grandchild(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 1, 6)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_grandparent(self, _name, node_type):
        root = basic.small(node_type)
        result = self.implementation(root, 6, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_itself(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 9, 9)
        self.assertIs(result, root.left.left.right)

    @_parameterize_by_node_type
    def test_medium_sibling(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 15, 14)
        self.assertIs(result, root.right.right)

    @_parameterize_by_node_type
    def test_medium_first_cousin(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 19, 21)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_medium_second_cousin(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 17, 21)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_third_cousin(self, _name, node_type):
        root = basic.medium(node_type)
        root = node_type(0, root.left, root.right)  # Make element=1 unique.
        result = self.implementation(root, 1, 18)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_child(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 7, 14)
        self.assertIs(result, root.right.right)

    @_parameterize_by_node_type
    def test_medium_parent(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 14, 7)
        self.assertIs(result, root.right.right)

    @_parameterize_by_node_type
    def test_medium_niece(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 11, 20)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_medium_aunt(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 20, 11)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_medium_first_cousin_once_removed_down(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 10, 17)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_first_cousin_once_removed_up(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 17, 10)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_second_cousin_once_removed_down(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 15, 16)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_second_cousin_once_removed_up(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 16, 15)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_grandchild(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 5, 21)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_medium_grandparent(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 21, 5)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_medium_great_niece(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 4, 20)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_great_aunt(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 20, 4)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_first_cousin_twice_removed_down(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 6, 18)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_first_cousin_twice_removed_up(self, _name, node_type):
        root = basic.medium(node_type)
        result = self.implementation(root, 18, 6)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_great_great_niece(self, _name, node_type):
        root = basic.medium(node_type)

        # Make element=3 unique.
        right = node_type(0, root.right.left, root.right.right)
        root = node_type(root.element, root.left, right)

        result = self.implementation(root, 0, 19)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_great_great_aunt(self, _name, node_type):
        root = basic.medium(node_type)

        # Make element=3 unique.
        right = node_type(0, root.right.left, root.right.right)
        root = node_type(root.element, root.left, right)

        result = self.implementation(root, 19, 0)
        self.assertIs(result, root)


@_parameterize_class_by_implementation(
    tree.is_bst,
    tree.is_bst_alt,
    tree.is_bst_iterative,
)
class TestIsBst(unittest.TestCase):
    """Test for functions to check if a binary tree is a binary search tree."""

    @_parameterize_by([trivial.empty, trivial.singleton], _NODE_TYPES)
    def test_trivial_is_bst(self, _name, factory, node_type):
        """Binary trees without multiple nodes are binary search trees."""
        root = factory(node_type)
        result = self.implementation(root)
        self.assertTrue(result)

    @_parameterize_by(_BASIC_TREE_FACTORIES, _NODE_TYPES)
    def test_basic_is_not_bst(self, _name, factory, node_type):
        """Trees in examples.basic are found not to be binary search trees."""
        root = factory(node_type)
        result = self.implementation(root)
        self.assertFalse(result)

    @_parameterize_by(_BST_TREE_FACTORIES, _NODE_TYPES)
    def test_bst_is_bst(self, _name, factory, node_type):
        root = factory(node_type)
        result = self.implementation(root)
        self.assertTrue(result)

    @_parameterize_by(_ALMOST_BST_TREE_FACTORIES, _NODE_TYPES)
    def test_almost_bst_is_not_bst(self, _name, factory, node_type):
        root = factory(node_type)
        result = self.implementation(root)
        self.assertFalse(result)


@_parameterize_class_by_implementation(
    tree.binary_search,
    tree.binary_search_iterative,
)
class TestBinarySearch(unittest.TestCase):
    """Tests for functions that find a node in a BST by bisection."""

    def test_empty_returns_none(self):
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root, 42)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_singleton_returns_none_if_absent(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root, 42)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_singleton_returns_node_if_present(self, _name, node_type):
        root = trivial.singleton(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by(_NODE_TYPES, [0, 1.5, 3], strict_names=False)
    def test_left_only_absent(self, _name, node_type, value):
        root = bst.left_only(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_left_only_at_root(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_left_only_at_child(self, _name, node_type):
        root = bst.left_only(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.left)

    @_parameterize_by(_NODE_TYPES, [0, 1.5, 3], strict_names=False)
    def test_right_only_absent(self, _name, node_type, value):
        root = bst.right_only(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_right_only_at_root(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_right_only_at_child(self, _name, node_type):
        root = bst.right_only(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.right)

    @_parameterize_by(_NODE_TYPES, [0, 1.5, 2.5, 4], strict_names=False)
    def test_tiny_absent(self, _name, node_type, value):
        root = bst.tiny(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_tiny_at_root(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_tiny_at_left(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_tiny_at_right(self, _name, node_type):
        root = bst.tiny(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.right)

    # FIXME: Write the rest of these tests.


if __name__ == '__main__':
    unittest.main()
