#!/usr/bin/env python

"""Tests for the tree module (subpackage)."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
import enum
from fractions import Fraction
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


class _NamedDict(dict):
    """A dict subclass that carries a "name" attribute."""

    __slots__ = ('name',)

    def __init__(self, name, /, *args, **kwargs):
        """Create a new named dictionary with the specified name."""
        super().__init__(*args, **kwargs)
        self.name = name

    def __repr__(self):
        """Python code representation, for debugging."""
        return f'{type(self).__name__}({self.name!r}, {super().__repr__()})'


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
    """Get the "__name__" or "name" attribute."""
    try:
        return thing.__name__
    except AttributeError:
        return thing.name


def _get_name_with_fallback(thing):
    """Get the  "__name__" or "name" attribute, with the str as a fallback."""
    try:
        return _get_name_no_fallback(thing)
    except AttributeError:
        return str(thing)


def _join_names(*arguments, indices=None, strict=True):
    """
    Join the names of each argument together by underscores.

    Each name is obtained by checking for a "__name__" attribute, followed by a
    "name" attribute. If any argument has neither, AttributeError is raised,
    unless strict=False, in which case, str is called on the argument.

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

    return parameterized.expand([
        (_join_names(*row, indices=name_indices, strict=strict_names), *row)
        for row in rows
    ])


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


def _parameterize_unequal_test(tree_factory_group):
    """
    Parameterize a test method on tree factory pairs and node types.

    This parameterizes tests that trees differing by structure or corresponding
    elements are found to be structurally unequal. Tree factories are not
    paired with themselves, since that would generate structurally equal trees.

    TestStructuralEqual.test_unequal_* methods use this function (see below).
    Unlike test_equal, TestStructuralEqual has several test_unequal* methods.
    This divides factories into groups to avoid generating too many test cases.
    Each group produces quadratically many tests; the sum of the squares of the
    group sizes is much smaller than the square of the sum of the group sizes.
    """
    def factories_are_distinct(lhs_factory, rhs_factory, *_):
        return lhs_factory is not rhs_factory

    return _parameterize_by(tree_factory_group,
                            tree_factory_group,
                            _NODE_TYPES,
                            _NODE_TYPES,
                            row_filter=factories_are_distinct)


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
    Tests that pairs of alternative linear searchers find the same nodes.

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


def _parameterize_absent_test(*values):
    """
    Parameterize a test method by node type and values to search for.

    This is used by tests in TestBinarySearch that search for absent values.
    """
    return _parameterize_by(_NODE_TYPES, values, strict_names=False)


@_parameterize_class_by_implementation(
    tree.binary_search,
    tree.binary_search_iterative,
)
class TestBinarySearch(unittest.TestCase):
    """
    Tests for functions that find a node in a binary search tree by bisection.

    These are tests for both the BST binary search functions. Those functions
    don't guarantee which nodes they find when there are multiple matches, but
    they do guarantee that they find the same node as each other. This class
    does not test for that; see TestBinarySearchConsistency below.

    Compared to TestLinearSearch, this class is more detailed, testing more
    hits and misses on some of the same trees. This is because there are more
    kinds of bugs that are likely to arise in binary search than linear search.
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

    @_parameterize_absent_test(0, 1.5, 3)
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

    @_parameterize_absent_test(0, 1.5, 3)
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

    @_parameterize_absent_test(0, 1.5, 2.5, 4)
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

    @_parameterize_absent_test(0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 8)
    def test_small_absent(self, _name, node_type, value):
        root = bst.small(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_at_root(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_at_left(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_at_left_left(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_at_left_right(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_at_right(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_at_right_left(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_small_at_right_right(self, _name, node_type):
        root = bst.small(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.right.right)

    @_parameterize_absent_test('h', 'j', 'm', 'q', 'sb', 'ta', 'tp', 'v')
    def test_small_str_absent(self, _name, node_type, value):
        root = bst.small_str(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_str_at_root(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'salamander')
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_str_at_left(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'lizard')
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_str_at_left_left(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'iguana')
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_str_at_left_right(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'newt')
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_str_at_right(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'tortoise')
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_str_at_right_left(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'snake')
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_small_str_at_right_right(self, _name, node_type):
        root = bst.small_str(node_type)
        result = self.implementation(root, 'turtle')
        self.assertIs(result, root.right.right)

    @_parameterize_absent_test(1, 2.5, 3.5, 4.5, 5.5, 6.5, 8)
    def test_small_no_left_left_absent(self, _name, node_type, value):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_left_left_at_root(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_no_left_left_at_left(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_no_left_left_at_left_right(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_no_left_left_at_right(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_no_left_left_at_right_left(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_small_no_left_left_at_right_right(self, _name, node_type):
        root = bst.small_no_left_left(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.right.right)

    @_parameterize_absent_test(0, 1.5, 3, 4.5, 5.5, 6.5, 8)
    def test_small_no_left_right_absent(self, _name, node_type, value):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_left_right_at_root(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_no_left_right_at_left(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_no_left_right_at_left_left(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_no_left_right_at_right(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_no_left_right_at_right_left(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_small_no_left_right_at_right_right(self, _name, node_type):
        root = bst.small_no_left_right(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.right.right)

    @_parameterize_absent_test(0, 1.5, 2.5, 3.5, 5, 6.5, 8)
    def test_small_no_right_left_absent(self, _name, node_type, value):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_right_left_at_root(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_no_right_left_at_left(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_no_right_left_at_left_left(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_no_right_left_at_left_right(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_no_right_left_at_right(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_no_right_left_at_right_right(self, _name, node_type):
        root = bst.small_no_right_left(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.right.right)

    @_parameterize_absent_test(0, 1.5, 2.5, 3.5, 4.5, 5.5, 7)
    def test_small_no_right_right_absent(self, _name, node_type, value):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_small_no_right_right_at_root(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_small_no_right_right_at_left(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_small_no_right_right_at_left_left(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, 1)
        self.assertIs(result, root.left.left)

    @_parameterize_by_node_type
    def test_small_no_right_right_at_left_right(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_small_no_right_right_at_right(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_small_no_right_right_at_right_left(self, _name, node_type):
        root = bst.small_no_right_right(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_left_chain_absent(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root, 1.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_left_chain_present(self, _name, node_type):
        root = bst.left_chain(node_type)
        result = self.implementation(root, 2)
        self.assertIs(result, root.left.left.left)

    @_parameterize_by_node_type
    def test_right_chain_absent(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root, 4.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_right_chain_present(self, _name, node_type):
        root = bst.right_chain(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root.right.right.right)

    @_parameterize_by_node_type
    def test_zigzag_chain_absent(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
        result = self.implementation(root, 3.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_zigzag_chain_present(self, _name, node_type):
        root = bst.zigzag_chain(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.right.left.right.left)

    @_parameterize_by_node_type
    def test_lefty_absent(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root, 1.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_lefty_present(self, _name, node_type):
        root = bst.lefty(node_type)
        result = self.implementation(root, 3)
        self.assertIs(result, root.left.left.left.right)

    @_parameterize_by_node_type
    def test_righty_absent(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root, 8.5)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_righty_present(self, _name, node_type):
        root = bst.righty(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.right.right.right.left)

    @_parameterize_absent_test(
        0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5,
        14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 22,
    )
    def test_medium_absent(self, _name, node_type, value):
        root = bst.medium(node_type)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    @_parameterize_by_node_type
    def test_medium_value_1(self, _name, node_type):
        root = bst.medium(node_type)
        expected = {root.left.left.left, root.left.left.left.left}
        result = self.implementation(root, 1)
        self.assertIn(result, expected)

    @_parameterize_by_node_type
    def test_medium_value_2(self, _name, node_type):
        root = bst.medium(node_type)
        expected = {root.left.left, root.left.left.left.right}
        result = self.implementation(root, 2)
        self.assertIn(result, expected)

    @_parameterize_by_node_type
    def test_medium_value_3(self, _name, node_type):
        root = bst.medium(node_type)
        expected = {root.left.left.right, root.left.left.right.right}
        result = self.implementation(root, 3)
        self.assertIn(result, expected)

    @_parameterize_by_node_type
    def test_medium_value_4(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 4)
        self.assertIs(result, root.left)

    @_parameterize_by_node_type
    def test_medium_value_5(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 5)
        self.assertIs(result, root.left.right.left.left)

    @_parameterize_by_node_type
    def test_medium_value_6(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 6)
        self.assertIs(result, root.left.right.left)

    @_parameterize_by_node_type
    def test_medium_value_7(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 7)
        self.assertIs(result, root.left.right.left.right)

    @_parameterize_by_node_type
    def test_medium_value_8(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 8)
        self.assertIs(result, root.left.right)

    @_parameterize_by_node_type
    def test_medium_value_9(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 9)
        self.assertIs(result, root.left.right.right.left)

    @_parameterize_by_node_type
    def test_medium_value_10(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 10)
        self.assertIs(result, root.left.right.right)

    @_parameterize_by_node_type
    def test_medium_value_11(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 11)
        self.assertIs(result, root)

    @_parameterize_by_node_type
    def test_medium_value_12(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 12)
        self.assertIs(result, root.right.left.left)

    @_parameterize_by_node_type
    def test_medium_value_13(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 13)
        self.assertIs(result, root.right.left)

    @_parameterize_by_node_type
    def test_medium_value_14(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 14)
        self.assertIs(result, root.right.left.right)

    @_parameterize_by_node_type
    def test_medium_value_15(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 15)
        self.assertIs(result, root.right)

    @_parameterize_by_node_type
    def test_medium_value_16(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 16)
        self.assertIs(result, root.right.right.left.left)

    @_parameterize_by_node_type
    def test_medium_value_17(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 17)
        self.assertIs(result, root.right.right.left)

    @_parameterize_by_node_type
    def test_medium_value_18(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 18)
        self.assertIs(result, root.right.right.left.right)

    @_parameterize_by_node_type
    def test_medium_value_19(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 19)
        self.assertIs(result, root.right.right)

    @_parameterize_by_node_type
    def test_medium_value_20(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 20)
        self.assertIs(result, root.right.right.right)

    @_parameterize_by_node_type
    def test_medium_value_21(self, _name, node_type):
        root = bst.medium(node_type)
        result = self.implementation(root, 21)
        self.assertIs(result, root.right.right.right.right)

    _HUGE_VALUE_LEVEL_896 = Fraction(
        '162026937765300092811580124535066267482048986570351077315406284829857'
        '646821547493233348223335871567929887608109652137465035422497105137592'
        '036570241135202062788433909851356359960048937612632893684957873908845'
        '434792886545138719978849537387522179513275072032036944132359120'
    )

    _HUGE_VALUE_LEVEL_900 = Fraction(
        '380478538857754430506070565758083460906167233530297994199460081219183'
        '141736393759468433558900401991298491832135595961179106244664788322958'
        '701466886412976919601224257364003438716911114573942239952549026512153'
        '6233457858649883128122272286958662272537764428784614064030004919'
    )

    @parameterized.expand([
        ('too_small', Fraction(0)),
        ('between_a', _HUGE_VALUE_LEVEL_896 + Fraction(1, 2)),
        ('between_b', _HUGE_VALUE_LEVEL_900 - Fraction(1, 2)),
        ('too_big', Fraction(2**900)),
    ])
    def test_huge_absent(self, _name, value):
        root = tree.lazy.LazyNode(1, 2**900)
        result = self.implementation(root, value)
        self.assertIsNone(result)

    def test_huge_present_level_896(self):
        expected_low = int(
            '16202693776530009281158012453506626748204898657035107731540628482'
            '98576468215474932333482233358715679298876081096521374650354224971'
            '05137592036570241135202062788433909851356359960048937612632893684'
            '95787390884543479288654513871997884953738752217951327507203203694'
            '4132359105'
        )
        expected_high = int(
            '16202693776530009281158012453506626748204898657035107731540628482'
            '98576468215474932333482233358715679298876081096521374650354224971'
            '05137592036570241135202062788433909851356359960048937612632893684'
            '95787390884543479288654513871997884953738752217951327507203203694'
            '4132359136'
        )
        expected = (expected_low, expected_high)

        root = tree.lazy.LazyNode(1, 2**900)
        result = self.implementation(root, self._HUGE_VALUE_LEVEL_896)

        with self.subTest('node has correct element'):
            self.assertEqual(result.element, self._HUGE_VALUE_LEVEL_896)

        with self.subTest('node roots correct subtree'):
            actual = (result.low, result.high)
            self.assertTupleEqual(actual, expected)

    @parameterized.expand([
        ('small', Fraction(1)),
        ('between', _HUGE_VALUE_LEVEL_900),
        ('big', Fraction(2**900 - 1)),
    ])
    def test_huge_present_level_900(self, _name, value):
        expected = (value, value + 1)

        root = tree.lazy.LazyNode(1, 2**900)
        result = self.implementation(root, value)

        with self.subTest('node has correct element'):
            self.assertEqual(result.element, value)

        with self.subTest('node roots correct subtree'):
            actual = (result.low, result.high)
            self.assertTupleEqual(actual, expected)

    @parameterized.expand([
        ('too_small', Fraction(0), 900),
        ('small', Fraction(1), 900),
        ('on_level_896', _HUGE_VALUE_LEVEL_896, 896),
        ('between_absent_a', _HUGE_VALUE_LEVEL_896 + Fraction(1, 2), 900),
        ('between_absent_b', _HUGE_VALUE_LEVEL_900 - Fraction(1, 2), 900),
        ('on_level_900', _HUGE_VALUE_LEVEL_900, 900),
        ('big', Fraction(2**900 - 1), 900),
        ('too_big', Fraction(2**900), 900),
    ])
    def test_huge_search_is_efficient(self, _name, value, min_access):
        """
        Binary search doesn't access more than height + 1 nodes.

        We always allow that many, even when fewer are needed. Traversing all
        the way down to the bottom or first mismatch (empty branch where the
        value would have to be) is valid. This is like implementing sequence
        binary search via bisect_left/bisect_right: it is a good strategy when
        the goal is to minimize comparisons in the average or worst case.
        """
        root = tree.lazy.LazyNode(1, 2**900)
        self.implementation(root, value)
        nodes_accessed = root.get_size_computed()

        if nodes_accessed < min_access:
            raise Exception(
                f'search not completed, {nodes_accessed=!s} < {min_access}')

        # We always allow up to height + 1 (even if fewer are needed).
        self.assertLessEqual(nodes_accessed, 900)


class TestBinarySearchConsistency(unittest.TestCase):
    """
    Tests that binary_search and binary_search_iterative find the same nodes.
    """

    @_parameterize_by_node_type
    def test_tiny_root_or_left_or_right(self, _name, node_type):
        """Binary searchers agree in a uniform 3-node 2-level bespoke tree."""
        root = node_type('hello', node_type('hello'), node_type('hello'))
        recursive_result = tree.binary_search(root, 'hello')
        iterative_result = tree.binary_search_iterative(root, 'hello')
        self._check_result_types(node_type, recursive_result, iterative_result)
        self.assertIs(recursive_result, iterative_result)

    @_parameterize_by_node_type
    def test_medium_leftmost_parent_or_left_child(self, _name, node_type):
        root = bst.medium(node_type)
        recursive_result = tree.binary_search(root, 1)
        iterative_result = tree.binary_search_iterative(root, 1)
        self._check_result_types(node_type, recursive_result, iterative_result)
        self.assertIs(recursive_result, iterative_result)

    @_parameterize_by_node_type
    def test_medium_leftmost_grandparent_or_left_right_grandchild(self, _name,
                                                                  node_type):
        root = bst.medium(node_type)
        recursive_result = tree.binary_search(root, 2)
        iterative_result = tree.binary_search_iterative(root, 2)
        self._check_result_types(node_type, recursive_result, iterative_result)
        self.assertIs(recursive_result, iterative_result)

    @_parameterize_by_node_type
    def test_medium_leftish_parent_or_right_child(self, _name, node_type):
        root = bst.medium(node_type)
        recursive_result = tree.binary_search(root, 3)
        iterative_result = tree.binary_search_iterative(root, 3)
        self._check_result_types(node_type, recursive_result, iterative_result)
        self.assertIs(recursive_result, iterative_result)

    def _check_result_types(self, node_type,
                            recursive_result, iterative_result):
        """Error out the test if any result is of the wrong type."""
        if recursive_result is None:
            raise Exception("recursive result is None, can't test consistency")

        if not isinstance(recursive_result, node_type):
            raise Exception(
                f'recursive result is {type(recursive_result).__name__!r},'
                f' need {node_type.__name__!r}')

        if iterative_result is None:
            raise Exception("iterative result is None, can't test consistency")

        if not isinstance(iterative_result, node_type):
            raise Exception(
                f'iterative result is {type(iterative_result).__name__!r},'
                f' need {node_type.__name__!r}')


@_parameterize_class_by_implementation(
    tree.binary_insert,
    tree.binary_insert_iterative,
)
class TestBinaryInsert(unittest.TestCase):
    """
    Tests for functions that insert a new node in a binary search tree.

    These tests apply separately to both of the BST insertion functions, and
    they do not rely on structural_equal/structural_equal_iterative.
    """

    _DENY_DUP = [
        _NamedDict('if deny dup implicit'),
        _NamedDict('if deny dup explicit', allow_duplicate=False),
    ]

    _DENY_AND_ALLOW_DUP = [
        *_DENY_DUP,
        _NamedDict('if allow dup', allow_duplicate=True)
    ]

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_empty_makes_singleton(self, _name, dup_kwargs):
        """
        Inserting into an empty "tree" returns a one-node tree of the element.
        """
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        result = self.implementation(root, 42, **dup_kwargs)

        with self.subTest('type'):
            self.assertIsInstance(result, tree.Node)
        with self.subTest('element'):
            self.assertEqual(result.element, 42)
        with self.subTest('left'):
            self.assertIsNone(result.left)
        with self.subTest('right'):
            self.assertIsNone(result.right)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_empty_creates_one_node(self, _name, dup_kwargs):
        root = trivial.empty(tree.Node)

        if root is not None:
            raise Exception(
                'trivial.empty is wrong, check it and other examples')

        with _Spy(tree.Node) as spy:
            self.implementation(root, 42, **dup_kwargs)

        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1, 2], strict_names=False)
    def test_singleton_same_root(self, _name, dup_kwargs, key):
        root = trivial.singleton(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_singleton_new_extends_bst_left(self, _name, dup_kwargs):
        """Inserting with a lesser key places the new node to the left."""
        expected = trivial.singleton(tree.Node)
        expected.left = tree.Node(0)
        root = trivial.singleton(tree.Node)
        self.implementation(root, 0, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_singleton_new_extends_bst_right(self, _name, dup_kwargs):
        """Inserting with a greater key places the new node to the right."""
        expected = trivial.singleton(tree.Node)
        expected.right = tree.Node(2)
        root = trivial.singleton(tree.Node)
        self.implementation(root, 2, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 2], strict_names=False)
    def test_singleton_new_creates_one_node(self, _name, dup_kwargs, key):
        root = trivial.singleton(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_DUP)
    def test_singleton_dup_makes_no_change(self, _name, dup_kwargs):
        root = trivial.singleton(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, 1, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(_DENY_DUP)
    def test_singleton_dup_creates_no_nodes(self, _name, dup_kwargs):
        root = trivial.singleton(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, 1, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_singleton_dup_extends_bst_if_allow_dup(self):
        """A duplicate node can become either branch of the existing node."""
        expected1 = trivial.singleton(tree.Node)
        expected1.left = tree.Node(1)
        expected2 = trivial.singleton(tree.Node)
        expected2.right = tree.Node(1)
        root = trivial.singleton(tree.Node)
        self.implementation(root, 1, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_singleton_dup_creates_one_node_if_allow_dup(self):
        root = trivial.singleton(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, 1, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1, 1.5, 2, 3],
                      strict_names=False)
    def test_left_only_same_root(self, _name, dup_kwargs, key):
        root = bst.left_only(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_left_only_new_extends_bst_left_left(self, _name, dup_kwargs):
        expected = bst.left_only(tree.Node)
        expected.left.left = tree.Node(0)
        root = bst.left_only(tree.Node)
        self.implementation(root, 0, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_left_only_new_extends_bst_left_right(self, _name, dup_kwargs):
        expected = bst.left_only(tree.Node)
        expected.left.right = tree.Node(1.5)
        root = bst.left_only(tree.Node)
        self.implementation(root, 1.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_left_only_new_extends_bst_right(self, _name, dup_kwargs):
        expected = bst.left_only(tree.Node)
        expected.right = tree.Node(3)
        root = bst.left_only(tree.Node)
        self.implementation(root, 3, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1.5, 3], strict_names=False)
    def test_left_only_new_creates_one_node(self, _name, dup_kwargs, key):
        root = bst.left_only(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_DUP, [1, 2], strict_names=False)
    def test_left_only_dup_makes_no_change(self, _name, dup_kwargs, key):
        root = bst.left_only(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, key, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(_DENY_DUP, [1, 2], strict_names=False)
    def test_left_only_dup_creates_no_nodes(self, _name, dup_kwargs, key):
        root = bst.left_only(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_left_only_dup_extends_bst_low_if_allow_dup(self):
        expected1 = bst.left_only(tree.Node)
        expected1.left.left = tree.Node(1)
        expected2 = bst.left_only(tree.Node)
        expected2.left.right = tree.Node(1)
        root = bst.left_only(tree.Node)
        self.implementation(root, 1, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_left_only_dup_extends_bst_high_if_allow_dup(self):
        expected1 = bst.left_only(tree.Node)
        expected1.left.right = tree.Node(2)
        expected2 = bst.left_only(tree.Node)
        expected2.right = tree.Node(2)
        root = bst.left_only(tree.Node)
        self.implementation(root, 2, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    @_parameterize_by([1, 2], strict_names=False)
    def test_left_only_dup_creates_one_node_if_allow_dup(self, _name, key):
        root = bst.left_only(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1, 1.5, 2, 3],
                      strict_names=False)
    def test_right_only_same_root(self, _name, dup_kwargs, key):
        root = bst.right_only(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_right_only_new_extends_bst_left(self, _name, dup_kwargs):
        expected = bst.right_only(tree.Node)
        expected.left = tree.Node(0)
        root = bst.right_only(tree.Node)
        self.implementation(root, 0, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_right_only_new_extends_bst_right_left(self, _name, dup_kwargs):
        expected = bst.right_only(tree.Node)
        expected.right.left = tree.Node(1.5)
        root = bst.right_only(tree.Node)
        self.implementation(root, 1.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_right_only_new_extends_bst_right_right(self, _name, dup_kwargs):
        expected = bst.right_only(tree.Node)
        expected.right.right = tree.Node(3)
        root = bst.right_only(tree.Node)
        self.implementation(root, 3, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1.5, 3], strict_names=False)
    def test_right_only_new_creates_one_node(self, _name, dup_kwargs, key):
        root = bst.right_only(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_DUP, [1, 2], strict_names=False)
    def test_right_only_dup_makes_no_change(self, _name, dup_kwargs, key):
        root = bst.right_only(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, key, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(_DENY_DUP, [1, 2], strict_names=False)
    def test_right_only_dup_creates_no_nodes(self, _name, dup_kwargs, key):
        root = bst.right_only(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_right_only_dup_extends_bst_low_if_allow_dup(self):
        expected1 = bst.right_only(tree.Node)
        expected1.left = tree.Node(1)
        expected2 = bst.right_only(tree.Node)
        expected2.right.left = tree.Node(1)
        root = bst.right_only(tree.Node)
        self.implementation(root, 1, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_right_only_dup_extends_bst_high_if_allow_dup(self):
        expected1 = bst.right_only(tree.Node)
        expected1.right.left = tree.Node(2)
        expected2 = bst.right_only(tree.Node)
        expected2.right.right = tree.Node(2)
        root = bst.right_only(tree.Node)
        self.implementation(root, 2, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    @_parameterize_by([1, 2], strict_names=False)
    def test_right_only_dup_creates_one_node_if_allow_dup(self, _name, key):
        root = bst.right_only(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1, 1.5, 2, 2.5, 3, 4],
                      strict_names=False)
    def test_tiny_same_root(self, _name, dup_kwargs, key):
        root = bst.tiny(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_tiny_new_extends_bst_left_left(self, _name, dup_kwargs):
        expected = bst.tiny(tree.Node)
        expected.left.left = tree.Node(0)
        root = bst.tiny(tree.Node)
        self.implementation(root, 0, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_tiny_new_extends_bst_left_right(self, _name, dup_kwargs):
        expected = bst.tiny(tree.Node)
        expected.left.right = tree.Node(1.5)
        root = bst.tiny(tree.Node)
        self.implementation(root, 1.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_tiny_new_extends_bst_right_left(self, _name, dup_kwargs):
        expected = bst.tiny(tree.Node)
        expected.right.left = tree.Node(2.5)
        root = bst.tiny(tree.Node)
        self.implementation(root, 2.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_tiny_new_extends_bst_right_right(self, _name, dup_kwargs):
        expected = bst.tiny(tree.Node)
        expected.right.right = tree.Node(4)
        root = bst.tiny(tree.Node)
        self.implementation(root, 4, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP, [0, 1.5, 2.5, 4],
                      strict_names=False)
    def test_tiny_new_creates_one_node(self, _name, dup_kwargs, key):
        root = bst.tiny(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_DUP, [1, 2, 3], strict_names=False)
    def test_tiny_dup_makes_no_change(self, _name, dup_kwargs, key):
        root = bst.tiny(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, key, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(_DENY_DUP, [1, 2, 3], strict_names=False)
    def test_tiny_dup_creates_no_nodes(self, _name, dup_kwargs, key):
        root = bst.tiny(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_tiny_dup_extends_bst_low_if_allow_dup(self):
        expected1 = bst.tiny(tree.Node)
        expected1.left.left = tree.Node(1)
        expected2 = bst.tiny(tree.Node)
        expected2.left.right = tree.Node(1)
        root = bst.tiny(tree.Node)
        self.implementation(root, 1, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_tiny_dup_extends_bst_mid_if_allow_dup(self):
        expected1 = bst.tiny(tree.Node)
        expected1.left.right = tree.Node(2)
        expected2 = bst.tiny(tree.Node)
        expected2.right.left = tree.Node(2)
        root = bst.tiny(tree.Node)
        self.implementation(root, 2, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_tiny_dup_extends_bst_high_if_allow_dup(self):
        expected1 = bst.tiny(tree.Node)
        expected1.right.left = tree.Node(3)
        expected2 = bst.tiny(tree.Node)
        expected2.right.right = tree.Node(3)
        root = bst.tiny(tree.Node)
        self.implementation(root, 3, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    @_parameterize_by([1, 2, 3], strict_names=False)
    def test_tiny_dup_creates_one_node_if_allow_dup(self, _name, key):
        root = bst.tiny(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(
        _DENY_AND_ALLOW_DUP,
        [0, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8],
        strict_names=False)
    def test_small_same_root(self, _name, dup_kwargs, key):
        root = bst.small(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_left_left_left(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.left.left.left = tree.Node(0)
        root = bst.small(tree.Node)
        self.implementation(root, 0, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_left_left_right(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.left.left.right = tree.Node(1.5)
        root = bst.small(tree.Node)
        self.implementation(root, 1.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_left_right_left(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.left.right.left = tree.Node(2.5)
        root = bst.small(tree.Node)
        self.implementation(root, 2.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_left_right_right(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.left.right.right = tree.Node(3.5)
        root = bst.small(tree.Node)
        self.implementation(root, 3.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_right_left_left(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.right.left.left = tree.Node(4.5)
        root = bst.small(tree.Node)
        self.implementation(root, 4.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_right_left_right(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.right.left.right = tree.Node(5.5)
        root = bst.small(tree.Node)
        self.implementation(root, 5.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_right_right_left(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.right.right.left = tree.Node(6.5)
        root = bst.small(tree.Node)
        self.implementation(root, 6.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_new_extends_bst_right_right_right(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        expected.right.right.right = tree.Node(8)
        root = bst.small(tree.Node)
        self.implementation(root, 8, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP,
                      [0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 8],
                      strict_names=False)
    def test_small_new_creates_one_node(self, _name, dup_kwargs, key):
        root = bst.small(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_DUP, [1, 2, 3, 4, 5, 6, 7], strict_names=False)
    def test_small_dup_makes_no_change(self, _name, dup_kwargs, key):
        root = bst.small(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, key, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(_DENY_DUP, [1, 2, 3, 4, 5, 6, 7], strict_names=False)
    def test_small_dup_creates_no_nodes(self, _name, dup_kwargs, key):
        root = bst.small(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_small_dup_extends_bst_1of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.left.left.left = tree.Node(1)
        expected2 = bst.small(tree.Node)
        expected2.left.left.right = tree.Node(1)
        root = bst.small(tree.Node)
        self.implementation(root, 1, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_dup_extends_bst_2of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.left.left.right = tree.Node(2)
        expected2 = bst.small(tree.Node)
        expected2.left.right.left = tree.Node(2)
        root = bst.small(tree.Node)
        self.implementation(root, 2, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_dup_extends_bst_3of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.left.right.left = tree.Node(3)
        expected2 = bst.small(tree.Node)
        expected2.left.right.right = tree.Node(3)
        root = bst.small(tree.Node)
        self.implementation(root, 3, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_dup_extends_bst_4of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.left.right.right = tree.Node(4)
        expected2 = bst.small(tree.Node)
        expected2.right.left.left = tree.Node(4)
        root = bst.small(tree.Node)
        self.implementation(root, 4, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_dup_extends_bst_5of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.right.left.left = tree.Node(5)
        expected2 = bst.small(tree.Node)
        expected2.right.left.right = tree.Node(5)
        root = bst.small(tree.Node)
        self.implementation(root, 5, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_dup_extends_bst_6of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.right.left.right = tree.Node(6)
        expected2 = bst.small(tree.Node)
        expected2.right.right.left = tree.Node(6)
        root = bst.small(tree.Node)
        self.implementation(root, 6, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_dup_extends_bst_7of7_if_allow_dup(self):
        expected1 = bst.small(tree.Node)
        expected1.right.right.left = tree.Node(7)
        expected2 = bst.small(tree.Node)
        expected2.right.right.right = tree.Node(7)
        root = bst.small(tree.Node)
        self.implementation(root, 7, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    @_parameterize_by([1, 2, 3, 4, 5, 6, 7], strict_names=False)
    def test_small_dup_creates_one_node_if_allow_dup(self, _name, key):
        root = bst.small(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(
        _DENY_AND_ALLOW_DUP,
        [
            'h', 'iguana', 'j', 'lizard', 'm', 'newt', 'q', 'salamander', 'sb',
            'snake', 'ta', 'tortoise', 'tp', 'turtle', 'v',
        ],
        strict_names=False)
    def test_small_str_same_root(self, _name, dup_kwargs, key):
        root = bst.small_str(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_left_left_left(self, _name, dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.left.left.left = tree.Node('h')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'h', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_left_left_right(self, _name,
                                                       dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.left.left.right = tree.Node('j')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'j', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_left_right_left(self, _name,
                                                       dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.left.right.left = tree.Node('m')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'm', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_left_right_right(self, _name,
                                                        dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.left.right.right = tree.Node('q')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'q', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_right_left_left(self, _name,
                                                       dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.right.left.left = tree.Node('sb')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'sb', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_right_left_right(self, _name,
                                                        dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.right.left.right = tree.Node('ta')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'ta', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_right_right_left(self, _name,
                                                        dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.right.right.left = tree.Node('tp')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'tp', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_str_new_extends_bst_right_right_right(self, _name,
                                                         dup_kwargs):
        expected = bst.small_str(tree.Node)
        expected.right.right.right = tree.Node('v')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'v', **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP,
                      ['h', 'j', 'm', 'q', 'sb', 'ta', 'tp', 'v'],
                      strict_names=False)
    def test_small_str_new_creates_one_node(self, _name, dup_kwargs, key):
        root = bst.small_str(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(
        _DENY_DUP,
        [
            'iguana', 'lizard', 'newt', 'salamander', 'snake', 'tortoise',
            'turtle',
        ],
        strict_names=False)
    def test_small_str_dup_makes_no_change(self, _name, dup_kwargs, key):
        root = bst.small_str(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, key, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(
        _DENY_DUP,
        [
            'iguana', 'lizard', 'newt', 'salamander', 'snake', 'tortoise',
            'turtle',
        ],
        strict_names=False)
    def test_small_str_dup_creates_no_nodes(self, _name, dup_kwargs, key):
        root = bst.small_str(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_small_str_dup_extends_bst_1of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.left.left.left = tree.Node('iguana')
        expected2 = bst.small_str(tree.Node)
        expected2.left.left.right = tree.Node('iguana')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'iguana', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_str_dup_extends_bst_2of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.left.left.right = tree.Node('lizard')
        expected2 = bst.small_str(tree.Node)
        expected2.left.right.left = tree.Node('lizard')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'lizard', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_str_dup_extends_bst_3of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.left.right.left = tree.Node('newt')
        expected2 = bst.small_str(tree.Node)
        expected2.left.right.right = tree.Node('newt')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'newt', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_str_dup_extends_bst_4of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.left.right.right = tree.Node('salamander')
        expected2 = bst.small_str(tree.Node)
        expected2.right.left.left = tree.Node('salamander')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'salamander', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_str_dup_extends_bst_5of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.right.left.left = tree.Node('snake')
        expected2 = bst.small_str(tree.Node)
        expected2.right.left.right = tree.Node('snake')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'snake', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_str_dup_extends_bst_6of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.right.left.right = tree.Node('tortoise')
        expected2 = bst.small_str(tree.Node)
        expected2.right.right.left = tree.Node('tortoise')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'tortoise', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_small_str_dup_extends_bst_7of7_if_allow_dup(self):
        expected1 = bst.small_str(tree.Node)
        expected1.right.right.left = tree.Node('turtle')
        expected2 = bst.small_str(tree.Node)
        expected2.right.right.right = tree.Node('turtle')
        root = bst.small_str(tree.Node)
        self.implementation(root, 'turtle', allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    @_parameterize_by(
        [
            'iguana', 'lizard', 'newt', 'salamander', 'snake', 'tortoise',
            'turtle',
        ],
        strict_names=False)
    def test_small_str_dup_creates_one_node_if_allow_dup(self, _name, key):
        root = bst.small_str(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_left_left_same_root(self, _name, dup_kwargs):
        root = bst.small_no_left_left(tree.Node)
        result = self.implementation(root, 1, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_left_left_new_extends_bst(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        root = bst.small_no_left_left(tree.Node)
        self.implementation(root, 1, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_left_left_new_creates_one_node(self, _name, dup_kwargs):
        root = bst.small_no_left_left(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, 1, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_left_right_same_root(self, _name, dup_kwargs):
        root = bst.small_no_left_right(tree.Node)
        result = self.implementation(root, 3, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_left_right_new_extends_bst(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        root = bst.small_no_left_right(tree.Node)
        self.implementation(root, 3, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_left_right_new_creates_one_node(self, _name, dup_kwargs):
        root = bst.small_no_left_right(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, 3, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_right_left_same_root(self, _name, dup_kwargs):
        root = bst.small_no_right_left(tree.Node)
        result = self.implementation(root, 5, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_right_left_new_extends_bst(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        root = bst.small_no_right_left(tree.Node)
        self.implementation(root, 5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_right_left_new_creates_one_node(self, _name, dup_kwargs):
        root = bst.small_no_right_left(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, 5, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_right_right_same_root(self, _name, dup_kwargs):
        root = bst.small_no_right_right(tree.Node)
        result = self.implementation(root, 7, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_right_right_new_extends_bst(self, _name, dup_kwargs):
        expected = bst.small(tree.Node)
        root = bst.small_no_right_right(tree.Node)
        self.implementation(root, 7, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_small_no_right_right_new_creates_one_node(self, _name,
                                                       dup_kwargs):
        root = bst.small_no_right_right(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, 7, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(
        _DENY_AND_ALLOW_DUP,
        [
            0, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5,
            9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5,
            16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 22,
        ],
        strict_names=False)
    def test_medium_same_root(self, _name, dup_kwargs, key):
        root = bst.medium(tree.Node)
        result = self.implementation(root, key, **dup_kwargs)
        self.assertIs(result, root)

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_left_left_left_left(self, _name,
                                                             dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.left.left.left.left = tree.Node(0)
        root = bst.medium(tree.Node)
        self.implementation(root, 0, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_left_left_right_left(self, _name,
                                                              dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.left.left.right.left = tree.Node(1.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 1.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_left_right_left(self, _name,
                                                         dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.left.right.left = tree.Node(2.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 2.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_left_right_right_right(self, _name,
                                                                dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.left.right.right.right = tree.Node(3.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 3.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_left_left_left(self, _name,
                                                              dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.left.left.left = tree.Node(4.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 4.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_left_left_right(self, _name,
                                                               dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.left.left.right = tree.Node(5.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 5.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_left_right_left(self, _name,
                                                               dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.left.right.left = tree.Node(6.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 6.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_left_right_right(self, _name,
                                                                dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.left.right.right = tree.Node(7.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 7.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_right_left_left(self, _name,
                                                               dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.right.left.left = tree.Node(8.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 8.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_right_left_right(self, _name,
                                                                dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.right.left.right = tree.Node(9.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 9.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_left_right_right_right(self, _name,
                                                           dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.left.right.right.right = tree.Node(10.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 10.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_left_left_left(self, _name,
                                                         dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.left.left.left = tree.Node(11.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 11.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_left_left_right(self, _name,
                                                          dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.left.left.right = tree.Node(12.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 12.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_left_right_left(self, _name,
                                                          dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.left.right.left = tree.Node(13.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 13.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_left_right_right(self, _name,
                                                           dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.left.right.right = tree.Node(14.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 14.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_left_left_left(self, _name,
                                                               dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.left.left.left = tree.Node(15.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 15.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_left_left_right(self, _name,
                                                                dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.left.left.right = tree.Node(16.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 16.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_left_right_left(self, _name,
                                                                dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.left.right.left = tree.Node(17.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 17.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_left_right_right(self, _name,
                                                                 dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.left.right.right = tree.Node(18.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 18.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_right_left(self, _name,
                                                           dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.right.left = tree.Node(19.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 19.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_right_right_left(self, _name,
                                                                 dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.right.right.left = tree.Node(20.5)
        root = bst.medium(tree.Node)
        self.implementation(root, 20.5, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(_DENY_AND_ALLOW_DUP)
    def test_medium_new_extends_bst_right_right_right_right_right(self, _name,
                                                                  dup_kwargs):
        expected = bst.medium(tree.Node)
        expected.right.right.right.right.right = tree.Node(22)
        root = bst.medium(tree.Node)
        self.implementation(root, 22, **dup_kwargs)
        self.assertEqual(repr(root), repr(expected))

    @_parameterize_by(
        _DENY_AND_ALLOW_DUP,
        [
            0, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5,
            13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 22,
        ],
        strict_names=False)
    def test_medium_new_creates_one_node(self, _name, dup_kwargs, key):
        root = bst.medium(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 1)

    @_parameterize_by(
        _DENY_DUP,
        [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21,
        ],
        strict_names=False)
    def test_medium_dup_makes_no_change(self, _name, dup_kwargs, key):
        root = bst.medium(tree.Node)
        expected_repr = repr(root)
        self.implementation(root, key, **dup_kwargs)
        self.assertEqual(repr(root), expected_repr)

    @_parameterize_by(
        _DENY_DUP,
        [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21,
        ],
        strict_names=False)
    def test_medium_dup_creates_no_nodes(self, _name, dup_kwargs, key):
        root = bst.medium(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, **dup_kwargs)
        self.assertEqual(spy.call_count, 0)

    def test_medium_dup_extends_bst_1of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.left.left.left.left = tree.Node(1)
        expected2 = bst.medium(tree.Node)
        expected2.left.left.left.left.right = tree.Node(1)
        expected3 = bst.medium(tree.Node)
        expected3.left.left.left.right.left = tree.Node(1)
        expected_reprs = {repr(expected1), repr(expected2), repr(expected3)}

        root = bst.medium(tree.Node)
        self.implementation(root, 1, allow_duplicate=True)
        self.assertIn(repr(root), expected_reprs)

    def test_medium_dup_extends_bst_2of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.left.left.right.left = tree.Node(2)
        expected2 = bst.medium(tree.Node)
        expected2.left.left.left.right.right = tree.Node(2)
        expected3 = bst.medium(tree.Node)
        expected3.left.left.right.left = tree.Node(2)
        expected_reprs = {repr(expected1), repr(expected2), repr(expected3)}

        root = bst.medium(tree.Node)
        self.implementation(root, 2, allow_duplicate=True)
        self.assertIn(repr(root), expected_reprs)

    def test_medium_extends_bst_3of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.left.right.left = tree.Node(3)
        expected2 = bst.medium(tree.Node)
        expected2.left.left.right.right.left = tree.Node(3)
        expected3 = bst.medium(tree.Node)
        expected3.left.left.right.right.right = tree.Node(3)
        expected_reprs = {repr(expected1), repr(expected2), repr(expected3)}

        root = bst.medium(tree.Node)
        self.implementation(root, 3, allow_duplicate=True)
        self.assertIn(repr(root), expected_reprs)

    def test_medium_extends_bst_4of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.left.right.right.right = tree.Node(4)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.left.left.left = tree.Node(4)
        root = bst.medium(tree.Node)
        self.implementation(root, 4, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_5of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.left.left.left = tree.Node(5)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.left.left.right = tree.Node(5)
        root = bst.medium(tree.Node)
        self.implementation(root, 5, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_6of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.left.left.right = tree.Node(6)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.left.right.left = tree.Node(6)
        root = bst.medium(tree.Node)
        self.implementation(root, 6, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_7of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.left.right.left = tree.Node(7)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.left.right.right = tree.Node(7)
        root = bst.medium(tree.Node)
        self.implementation(root, 7, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_8of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.left.right.right = tree.Node(8)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.right.left.left = tree.Node(8)
        root = bst.medium(tree.Node)
        self.implementation(root, 8, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_9of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.right.left.left = tree.Node(9)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.right.left.right = tree.Node(9)
        root = bst.medium(tree.Node)
        self.implementation(root, 9, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_10of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.right.left.right = tree.Node(10)
        expected2 = bst.medium(tree.Node)
        expected2.left.right.right.right = tree.Node(10)
        root = bst.medium(tree.Node)
        self.implementation(root, 10, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_11of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.left.right.right.right = tree.Node(11)
        expected2 = bst.medium(tree.Node)
        expected2.right.left.left.left = tree.Node(11)
        root = bst.medium(tree.Node)
        self.implementation(root, 11, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_12of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.left.left.left = tree.Node(12)
        expected2 = bst.medium(tree.Node)
        expected2.right.left.left.right = tree.Node(12)
        root = bst.medium(tree.Node)
        self.implementation(root, 12, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_13of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.left.left.right = tree.Node(13)
        expected2 = bst.medium(tree.Node)
        expected2.right.left.right.left = tree.Node(13)
        root = bst.medium(tree.Node)
        self.implementation(root, 13, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_14of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.left.right.left = tree.Node(14)
        expected2 = bst.medium(tree.Node)
        expected2.right.left.right.right = tree.Node(14)
        root = bst.medium(tree.Node)
        self.implementation(root, 14, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_15of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.left.right.right = tree.Node(15)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.left.left.left = tree.Node(15)
        root = bst.medium(tree.Node)
        self.implementation(root, 15, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_16of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.right.left.left.left = tree.Node(16)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.left.left.right = tree.Node(16)
        root = bst.medium(tree.Node)
        self.implementation(root, 16, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_17of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.right.left.left.right = tree.Node(17)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.left.right.left = tree.Node(17)
        root = bst.medium(tree.Node)
        self.implementation(root, 17, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_18of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.right.left.right.left = tree.Node(18)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.left.right.right = tree.Node(18)
        root = bst.medium(tree.Node)
        self.implementation(root, 18, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_19of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.right.left.right.right = tree.Node(19)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.right.left = tree.Node(19)
        root = bst.medium(tree.Node)
        self.implementation(root, 19, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_20of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.right.right.left = tree.Node(20)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.right.right.left = tree.Node(20)
        root = bst.medium(tree.Node)
        self.implementation(root, 20, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    def test_medium_extends_bst_21of21_if_allow_dup(self):
        expected1 = bst.medium(tree.Node)
        expected1.right.right.right.right.left = tree.Node(21)
        expected2 = bst.medium(tree.Node)
        expected2.right.right.right.right.right = tree.Node(21)
        root = bst.medium(tree.Node)
        self.implementation(root, 21, allow_duplicate=True)
        self.assertIn(repr(root), {repr(expected1), repr(expected2)})

    @_parameterize_by(
        [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21,
        ],
        strict_names=False)
    def test_medium_dup_creates_one_node_if_allow_dup(self, _name, key):
        root = bst.medium(tree.Node)
        with _Spy(tree.Node) as spy:
            self.implementation(root, key, allow_duplicate=True)
        self.assertEqual(spy.call_count, 1)


class TestBinaryInsertConsistency(unittest.TestCase):
    """
    Tests that binary_insert and binary_insert_iterative give the same trees.

    That is, this tests that the BST insertion implementations each choose the
    same insertion points, when given the same tree and the same new key to
    insert. Usually, there is only one correct insertion point; see the
    binary_insert_iterative docstring about when there are more than one.

    These tests always tests both the BST insertion functions together, and
    they do not rely on structural_equal/structural_equal_iterative.
    """

    def test_singleton(self):
        root_recursive, root_iterative = self._run_both(trivial.singleton, 1)
        self.assertEqual(repr(root_recursive), repr(root_iterative))

    @_parameterize_by([bst.left_only, bst.right_only], [1, 2],
                      strict_names=False)
    def test_pair(self, _name, factory, key):
        root_recursive, root_iterative = self._run_both(factory, key)
        self.assertEqual(repr(root_recursive), repr(root_iterative))

    @_parameterize_by([1, 2, 3], strict_names=False)
    def test_tiny(self, _name, key):
        root_recursive, root_iterative = self._run_both(bst.tiny, key)
        self.assertEqual(repr(root_recursive), repr(root_iterative))

    @_parameterize_by([1, 2, 3, 4, 5, 6, 7], strict_names=False)
    def test_small(self, _name, key):
        root_recursive, root_iterative = self._run_both(bst.small, key)
        self.assertEqual(repr(root_recursive), repr(root_iterative))

    @_parameterize_by(
        [
            'iguana', 'lizard', 'newt', 'salamander', 'snake', 'tortoise',
            'turtle',
        ],
        strict_names=False)
    def test_small_str(self, _name, key):
        root_recursive, root_iterative = self._run_both(bst.small_str, key)
        self.assertEqual(repr(root_recursive), repr(root_iterative))

    @_parameterize_by(
        [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21,
        ],
        strict_names=False)
    def test_medium(self, _name, key):
        root_recursive, root_iterative = self._run_both(bst.medium, key)
        self.assertEqual(repr(root_recursive), repr(root_iterative))

    @staticmethod
    def _run_both(factory, key):
        """
        Make two trees and insert the key into them with both implementations.

        The insertion allows duplicates, and that it creates exactly one node
        is checked. The trees, after insertions and those checks, are returned.
        """
        root_recursive = factory(tree.Node)
        with _Spy(tree.Node) as spy:
            tree.binary_insert(root_recursive, key, allow_duplicate=True)
        if spy.call_count != 1:
            raise Exception(f'binary_insert: {spy.call_count=}, should be 1')

        root_iterative = factory(tree.Node)
        with _Spy(tree.Node) as spy:
            tree.binary_insert_iterative(root_iterative, key,
                                         allow_duplicate=True)
        if spy.call_count != 1:
            raise Exception(
                f'binary_insert_iterative: {spy.call_count=}, should be 1')

        return root_recursive, root_iterative


# TODO: Write classes with special versions of the repr-comparing tests from
# the above two classes (note: not all the tests in TestBinaryInsert compare
# reprs). The new tests will use structural_equal/structural_equal_iterative
# instead of comparing reprs. Call the classes TestBinaryInsertStructuralEqual
# and TestBinaryInsertConsistencyStructuralEqual.


class TestBuildBst(unittest.TestCase):
    """Tests for the build_bst function."""

    @parameterized.expand([
        ('seq', []),
        ('iter', iter([])),
    ])
    def test_empty(self, _name, iterable):
        result = tree.build_bst(iterable)
        self.assertIsNone(result)

    @parameterized.expand([
        ('seq', [42]),
        ('iter', iter([42])),
    ])
    def test_singleton(self, _name, iterable):
        result = tree.build_bst(iterable)

        with self.subTest('type'):
            self.assertIsInstance(result, tree.Node)
        with self.subTest('element'):
            self.assertEqual(result.element, 42)
        with self.subTest('left'):
            self.assertIsNone(result.left)
        with self.subTest('right'):
            self.assertIsNone(result.right)

    @parameterized.expand([
        ('low_high_seq', [1, 2]),
        ('low_high_iter', iter([1, 2])),
        ('high_low_seq', [2, 1]),
        ('high_low_iter', iter([2, 1])),
    ])
    def test_pair(self, _name, iterable):
        expected1 = bst.left_only(tree.Node)
        expected2 = bst.right_only(tree.Node)
        result = tree.build_bst(iterable)
        self.assertIn(repr(result), {repr(expected1), repr(expected2)})

    @parameterized.expand([
        ('123_seq', [1, 2, 3]),
        ('123_iter', iter([1, 2, 3])),
        ('132_seq', [1, 3, 2]),
        ('132_iter', iter([1, 3, 2])),
        ('213_seq', [2, 1, 3]),
        ('213_iter', iter([2, 1, 3])),
        ('231_seq', [2, 3, 1]),
        ('231_iter', iter([2, 3, 1])),
        ('312_seq', [3, 1, 2]),
        ('312_iter', iter([3, 1, 2])),
        ('321_seq', [3, 2, 1]),
        ('321_iter', iter([3, 2, 1])),
    ])
    def test_triple(self, _name, iterable):
        t = tree.Node

        expected_reprs = {repr(expected) for expected in [
            t(1, None, t(2, None, t(3))),
            t(1, None, t(3, t(2), None)),
            t(2, t(1), t(3)),
            t(3, t(1, None, t(2)), None),
            t(3, t(2, t(1), None), None),
        ]}

        result = tree.build_bst(iterable)
        self.assertIn(repr(result), expected_reprs)

    @parameterized.expand([
        ('1234_seq', [1, 2, 3, 4]),
        ('1234_iter', iter([1, 2, 3, 4])),
        ('1243_seq', [1, 2, 4, 3]),
        ('1243_iter', iter([1, 2, 4, 3])),
        ('1324_seq', [1, 3, 2, 4]),
        ('1324_iter', iter([1, 3, 2, 4])),
        ('1342_seq', [1, 3, 4, 2]),
        ('1342_iter', iter([1, 3, 4, 2])),
        ('1423_seq', [1, 4, 2, 3]),
        ('1423_iter', iter([1, 4, 2, 3])),
        ('1432_seq', [1, 4, 3, 2]),
        ('1432_iter', iter([1, 4, 3, 2])),

        ('2134_seq', [2, 1, 3, 4]),
        ('2134_iter', iter([2, 1, 3, 4])),
        ('2143_seq', [2, 1, 4, 3]),
        ('2143_iter', iter([2, 1, 4, 3])),
        ('2314_seq', [2, 3, 1, 4]),
        ('2314_iter', iter([2, 3, 1, 4])),
        ('2341_seq', [2, 3, 4, 1]),
        ('2341_iter', iter([2, 3, 4, 1])),
        ('2413_seq', [2, 4, 1, 3]),
        ('2413_iter', iter([2, 4, 1, 3])),
        ('2431_seq', [2, 4, 3, 1]),
        ('2431_iter', iter([2, 4, 3, 1])),

        ('3124_seq', [3, 1, 2, 4]),
        ('3124_iter', iter([3, 1, 2, 4])),
        ('3142_seq', [3, 1, 4, 2]),
        ('3142_iter', iter([3, 1, 4, 2])),
        ('3214_seq', [3, 2, 1, 4]),
        ('3214_iter', iter([3, 2, 1, 4])),
        ('3241_seq', [3, 2, 4, 1]),
        ('3241_iter', iter([3, 2, 4, 1])),
        ('3412_seq', [3, 4, 1, 2]),
        ('3412_iter', iter([3, 4, 1, 2])),
        ('3421_seq', [3, 4, 2, 1]),
        ('3421_iter', iter([3, 4, 2, 1])),

        ('4123_seq', [4, 1, 2, 3]),
        ('4123_iter', iter([4, 1, 2, 3])),
        ('4132_seq', [4, 1, 3, 2]),
        ('4132_iter', iter([4, 1, 3, 2])),
        ('4213_seq', [4, 2, 1, 3]),
        ('4213_iter', iter([4, 2, 1, 3])),
        ('4231_seq', [4, 2, 3, 1]),
        ('4231_iter', iter([4, 2, 3, 1])),
        ('4312_seq', [4, 3, 1, 2]),
        ('4312_iter', iter([4, 3, 1, 2])),
        ('4321_seq', [4, 3, 2, 1]),
        ('4321_iter', iter([4, 3, 2, 1])),
    ])
    def test_quad(self, _name, iterable):
        t = tree.Node

        expected_reprs = {repr(expected) for expected in [
            t(1, None, t(2, None, t(3, None, t(4)))),
            t(1, None, t(2, None, t(4, t(3), None))),
            t(1, None, t(3, t(2), t(4))),
            t(1, None, t(4, t(2, None, t(3)), None)),
            t(1, None, t(4, t(3, t(2), None), None)),
            t(2, t(1), t(3, None, t(4))),
            t(2, t(1), t(4, t(3), None)),
            t(3, t(1, None, t(2)), t(4)),
            t(3, t(2, t(1), None), t(4)),
            t(4, t(1, None, t(2, None, t(3))), None),
            t(4, t(1, None, t(3, t(2), None)), None),
            t(4, t(2, t(1), t(3)), None),
            t(4, t(3, t(1, None, t(2)), None), None),
            t(4, t(3, t(2, t(1), None), None), None),
        ]}

        result = tree.build_bst(iterable)
        self.assertIn(repr(result), expected_reprs)

    # FIXME: Reorganize the above test(s) in this class and write the rest.


if __name__ == '__main__':
    unittest.main()
