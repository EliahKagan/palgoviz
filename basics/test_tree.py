"""Tests for tree.py."""

import unittest

from tree import Node


@unittest.skip(  # FIXME: Make and implementation a decision and remove @skip.
    'Unsure if these construction requirements make a useful exercise.')
class TestNode(unittest.TestCase):
    """
    Tests for the Node class.

    In this class, an internal node with no right child is a "lefter" and an
    internal node with no left child is a "righter." This terminology is not at
    all standard and may not often be justified, but here I think it makes the
    test names much more readable. Likewise a "full" node is one with two
    children, which is slightly less strange since a full binary tree is one
    whose internal nodes are all "full" in this sense, but still not standard.
    """

    def test_can_construct_leaf_without_child_args(self):
        leaf = Node(10)
        with self.subTest(attribute='element'):
            self.assertEqual(leaf.element, 10)
        with self.subTest(attribute='left'):
            self.assertIsNone(leaf.left)
        with self.subTest(attribute='right'):
            self.assertIsNone(leaf.right)

    def test_can_construct_leaf_with_both_child_positional_args(self):
        leaf = Node(10, None, None)
        with self.subTest(attribute='element'):
            self.assertEqual(leaf.element, 10)
        with self.subTest(attribute='left'):
            self.assertIsNone(leaf.left)
        with self.subTest(attribute='right'):
            self.assertIsNone(leaf.right)

    def test_can_construct_leaf_with_child_keyword_args_left_right(self):
        leaf = Node(10, left=None, right=None)
        with self.subTest(attribute='element'):
            self.assertEqual(leaf.element, 10)
        with self.subTest(attribute='left'):
            self.assertIsNone(leaf.left)
        with self.subTest(attribute='right'):
            self.assertIsNone(leaf.right)

    def test_can_construct_leaf_with_child_keyword_args_right_left(self):
        leaf = Node(10, right=None, left=None)
        with self.subTest(attribute='element'):
            self.assertEqual(leaf.element, 10)
        with self.subTest(attribute='left'):
            self.assertIsNone(leaf.left)
        with self.subTest(attribute='right'):
            self.assertIsNone(leaf.right)

    def test_can_construct_leaf_with_left_child_keyword_arg(self):
        leaf = Node(10, left=None)
        with self.subTest(attribute='element'):
            self.assertEqual(leaf.element, 10)
        with self.subTest(attribute='left'):
            self.assertIsNone(leaf.left)
        with self.subTest(attribute='right'):
            self.assertIsNone(leaf.right)

    def test_can_construct_leaf_with_right_child_keyword_arg(self):
        leaf = Node(10, right=None)
        with self.subTest(attribute='element'):
            self.assertEqual(leaf.element, 10)
        with self.subTest(attribute='left'):
            self.assertIsNone(leaf.left)
        with self.subTest(attribute='right'):
            self.assertIsNone(leaf.right)

    def test_cannot_construct_leaf_with_single_child_positional_arg(self):
        with self.assertRaises(TypeError):
            Node(10, None)

    def test_cannot_construct_leaf_with_mixed_child_args(self):
        """Children, if given, must both be positional or both be keywords."""
        with self.subTest(keyword_child='left'):
            with self.assertRaises(TypeError):
                Node(10, None, left=None)

        with self.subTest(keyword_child='right'):
            with self.assertRaises(TypeError):
                Node(10, None, right=None)

    def test_can_construct_lefter_with_both_child_positional_args(self):
        left = Node(20)
        root = Node(10, left, None)
        with self.subTest(attribute='element'):
            self.assertEqual(root.element, 10)
        with self.subTest(attribute='left'):
            self.assertIs(root.left, left)
        with self.subTest(attribute='right'):
            self.assertIsNone(root.right)

    def test_can_construct_lefter_with_left_child_keyword_arg(self):
        left = Node(20)
        root = Node(10, left=left)
        with self.subTest(attribute='element'):
            self.assertEqual(root.element, 10)
        with self.subTest(attribute='left'):
            self.assertIs(root.left, left)
        with self.subTest(attribute='right'):
            self.assertIsNone(root.right)

    def test_can_construct_lefter_with_child_keyword_args_left_right(self):
        left = Node(20)
        root = Node(10, left=left, right=None)
        with self.subTest(attribute='element'):
            self.assertEqual(root.element, 10)
        with self.subTest(attribute='left'):
            self.assertIs(root.left, left)
        with self.subTest(attribute='right'):
            self.assertIsNone(root.right)

    def test_can_construct_lefter_with_child_keyword_args_right_left(self):
        left = Node(20)
        root = Node(10, right=None, left=left)
        with self.subTest(attribute='element'):
            self.assertEqual(root.element, 10)
        with self.subTest(attribute='left'):
            self.assertIs(root.left, left)
        with self.subTest(attribute='right'):
            self.assertIsNone(root.right)

    # FIXME: Write the rest of these construction tests.

    def test_repr_of_leaf_is_code_omitting_children(self):
        leaf = Node(10)

    def test_repr_of_internal_node_is_code_including_children(self):
        root = Node(10, Node(20), Node(30))

    # FIXME: Write the rest of the tests that are not about construction.
