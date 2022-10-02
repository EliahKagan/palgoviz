#!/usr/bin/env python

"""Tests for sll.py."""

import abc
import gc
import itertools
import types
import unittest
import weakref

import graphviz
from parameterized import parameterized

import sll
import testing


class _TestNodeBase(abc.ABC):
    """Base class providing shared tests of sll.Node and sll.TypedNode."""

    @property
    @abc.abstractmethod
    def impl(self):
        """The implementation of a hash-consing SLL node class under test."""
        raise NotImplementedError

    def test_cannot_construct_with_zero_args(self):
        with self.assertRaises(TypeError):
            self.impl()

    def test_can_construct_with_one_arg(self):
        head = self.impl('foo')
        self.assertIsInstance(head, self.impl)

    def test_constructing_with_one_arg_has_value(self):
        head = self.impl('foo')
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_one_arg_has_no_next_node(self):
        head = self.impl('foo')
        self.assertIsNone(head.next_node)

    def test_cannot_construct_with_second_arg_not_of_node_type(self):
        """
        The second argument (next_node) must be an instance of the node type.

        Since we are doing hash consing, the effects of allowing a next_node of
        the wrong type are dire: the wrong behavior is both unintuitive and
        global. So it is important to check the type of next_node, even if
        runtime type-checking is not otherwise called for.
        """
        with self.assertRaises(TypeError):
            self.impl('foo', object())

    def test_can_construct_with_two_args_second_none(self):
        head = self.impl('foo', None)
        self.assertIsInstance(head, self.impl)

    def test_constructing_with_two_args_second_none_has_value(self):
        head = self.impl('foo', None)
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_two_args_second_none_has_no_next_node(self):
        head = self.impl('foo', None)
        self.assertIsNone(head.next_node)

    def test_can_construct_with_two_args_second_node(self):
        head = self.impl('foo', self.impl('bar'))
        self.assertIsInstance(head, self.impl)

    def test_constructing_with_two_args_second_node_has_value(self):
        head = self.impl('foo', self.impl('bar'))
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_two_args_second_node_has_it_as_next_node(self):
        next_node = self.impl('bar')
        head = self.impl('foo', next_node)
        self.assertIs(head.next_node, next_node)

    def test_value_attribute_is_read_only(self):
        """The value attribute cannot be written."""
        head = self.impl('foo')
        with self.assertRaises(AttributeError):
            head.value = 'bar'

    def test_value_attribute_cannot_be_deleted(self):
        head = self.impl('foo')
        with self.assertRaises(AttributeError):
            del head.value

    def test_next_node_attribute_is_read_only_if_none(self):
        """The next_node attribute cannot be written."""
        head = self.impl('foo')
        with self.assertRaises(AttributeError):
            head.next_node = self.impl('baz')

    def test_next_node_attribute_is_read_only_if_not_none(self):
        """The next_node attribute cannot be written."""
        head = self.impl('foo', self.impl('bar'))
        with self.assertRaises(AttributeError):
            head.next_node = self.impl('baz')

    def test_next_node_attribute_cannot_be_deleted_if_none(self):
        head = self.impl('foo')
        with self.assertRaises(AttributeError):
            del head.next_node

    def test_next_node_attribute_cannot_be_deleted_if_not_none(self):
        head = self.impl('foo', self.impl('bar'))
        with self.assertRaises(AttributeError):
            del head.next_node

    def test_new_attributes_cannot_be_created(self):
        head = self.impl('foo')
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
        head = self.impl('foo')
        with self.assertRaises(AttributeError):
            head.__dict__

    @abc.abstractmethod
    def test_repr_shows_no_next_node_if_none(self):
        """
        The repr is a function call expression, omitting next_node if None.

        This test method is abstract n _TestNodeBase so it can be overridden in
        derived classes to make assertions with hard-coded strings, to be
        clearer what the exact expected result is, and to avoid duplicating
        logic between the tests and the code under test.

        The same applies to test_repr_shows_chain_recursively below.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def test_repr_shows_chain_recursively(self):
        """
        The repr is a function call expression, containing the next_node repr.

        See test_repr_shows_no_next_node_if_none on why it and this method are
        abstract in _TestNodeBase.
        """
        raise NotImplementedError

    @parameterized.expand([
        ('one', 1),
        ('zero', 0),
        ('obj', object()),
        ('none', None),
    ])
    def test_is_truthy(self, _name, value):
        head = self.impl(value)
        self.assertTrue(head)

    def test_nodes_holding_same_type_value_no_next_are_equal(self):
        lhs = self.impl('foo')
        rhs = self.impl('foo')
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_same_type_value_no_next_are_identical(self):
        lhs = self.impl('foo')
        rhs = self.impl('foo')
        self.assertIs(lhs, rhs)

    def test_nodes_holding_same_type_value_next_are_equal(self):
        lhs = self.impl('foo', self.impl('bar'))
        rhs = self.impl('foo', self.impl('bar'))
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_same_type_value_next_are_identical(self):
        lhs = self.impl('foo', self.impl('bar'))
        rhs = self.impl('foo', self.impl('bar'))
        self.assertIs(lhs, rhs)

    def test_nodes_heading_same_type_value_chain_are_equal(self):
        lhs = self.impl('a', self.impl('b', self.impl('c', self.impl('d'))))
        rhs = self.impl('a', self.impl('b', self.impl('c', self.impl('d'))))
        self.assertEqual(lhs, rhs)

    def test_nodes_heading_same_type_value_chain_are_identical(self):
        lhs = self.impl('a', self.impl('b', self.impl('c', self.impl('d'))))
        rhs = self.impl('a', self.impl('b', self.impl('c', self.impl('d'))))
        self.assertIs(lhs, rhs)

    def test_nodes_heading_different_values_no_next_are_not_equal(self):
        lhs = self.impl('foo')
        rhs = self.impl('bar')
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_different_values_no_next_are_not_identical(self):
        lhs = self.impl('foo')
        rhs = self.impl('bar')
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_different_values_same_next_are_not_equal(self):
        lhs = self.impl('foo', self.impl('baz'))
        rhs = self.impl('bar', self.impl('baz'))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_different_values_same_next_are_not_identical(self):
        lhs = self.impl('foo', self.impl('baz'))
        rhs = self.impl('bar', self.impl('baz'))
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_same_values_different_next_are_not_equal(self):
        lhs = self.impl('foo', self.impl('bar'))
        rhs = self.impl('foo', self.impl('baz'))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_same_values_different_next_are_not_identical(self):
        lhs = self.impl('foo', self.impl('bar'))
        rhs = self.impl('foo', self.impl('baz'))
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_different_length_chains_are_not_equal(self):
        shorter = self.impl('foo')
        longer = self.impl('foo', self.impl('bar'))
        with self.subTest(lhs='shorter', rhs='longer'):
            self.assertNotEqual(shorter, longer)
        with self.subTest(lhs='longer', rhs='shorter'):
            self.assertNotEqual(longer, shorter)

    def test_nodes_heading_different_length_chains_are_not_identical(self):
        shorter = self.impl('foo')
        longer = self.impl('foo', self.impl('bar'))
        with self.subTest(lhs='shorter', rhs='longer'):
            self.assertIsNot(shorter, longer)
        with self.subTest(lhs='longer', rhs='shorter'):
            self.assertIsNot(longer, shorter)

    def test_from_iterable_returns_none_from_empty_sequence(self):
        head = self.impl.from_iterable([])
        self.assertIsNone(head)

    def test_from_iterable_returns_none_from_empty_iterator(self):
        head = self.impl.from_iterable(iter([]))
        self.assertIsNone(head)

    def test_from_iterable_finds_chain_from_nonempty_sequence(self):
        # NOTE: This test MUST be written to assign "expected" first.
        expected = self.impl(
            'a', self.impl('b', self.impl('c', self.impl('d'))))
        actual = self.impl.from_iterable('abcd')
        self.assertIs(actual, expected)

    def test_from_iterable_builds_chain_from_nonempty_sequence(self):
        # NOTE: This test MUST be written to assign "actual" first.
        actual = self.impl.from_iterable('abcd')
        expected = self.impl(
            'a', self.impl('b', self.impl('c', self.impl('d'))))
        self.assertIs(actual, expected)

    def test_from_iterable_builds_long_chain(self):
        head = self.impl.from_iterable(range(9000))
        self.assertIsInstance(head, self.impl)

    def test_from_iterable_long_chain_has_same_length_as_input(self):
        head = self.impl.from_iterable(range(9000))

        length = 0
        node = head
        while node:
            length += 1
            node = node.next_node

        self.assertEqual(length, 9000)

    def test_from_iterable_long_chain_has_equal_values_to_input(self):
        head = self.impl.from_iterable(range(9000))

        values = []
        node = head
        while node:
            values.append(node.value)
            node = node.next_node

        self.assertListEqual(values, list(range(9000)))

    def test_from_iterable_new_longer_chain_can_overlap_long_chain(self):
        shorter = self.impl.from_iterable(range(9000))
        longer = self.impl.from_iterable(range(-100, 9000))

        node = longer
        for _ in range(100):
            node = node.next_node

        self.assertIs(node, shorter)

    def test_from_iterable_new_shorter_chain_can_overlap_long_chain(self):
        longer = self.impl.from_iterable(range(-100, 9000))
        shorter = self.impl.from_iterable(range(9000))

        node = longer
        for _ in range(100):
            node = node.next_node

        self.assertIs(node, shorter)

    @parameterized.expand(['__eq__', '__ne__', '__hash__'])
    def test_type_uses_reference_equality_comparison(self, name):
        expected = getattr(object, name)
        actual = getattr(self.impl, name)
        self.assertIs(actual, expected)

    def test_no_more_nodes_are_maintained_than_necessary(self):
        """
        Nodes are always shared and allowed to be collected when unreachable.

        To a greater extent than other tests in this test module, these tests
        assume no other code in the same test runner process has created and
        *kept* references to Node instances. Unless some other code in the
        project does so and is under test, this is unlikely to be a problem.

        Note also that these tests rely on the count_instances method being
        correctly implemented. But it is fairly unlikely that an unintentional
        bug in that method would cause all tests to wrongly pass.
        """
        head1 = self.impl('a', self.impl('b', self.impl('c', self.impl('d'))))
        head2 = self.impl('x', self.impl('b', self.impl('c', self.impl('d'))))
        head3 = self.impl(0)
        head4 = self.impl.from_iterable(range(9000))

        with self.subTest('before any of head1-head5 are collectable'):
            testing.collect_if_not_ref_counting()
            self.assertEqual(self.impl.count_instances(), 9006)

        head5 = self.impl.from_iterable(range(-100, 9000))

        with self.subTest('after creating head5'):
            # We do not need to force a collection here regardless of platform,
            # since we have only created nodes since the last possibly forced
            # collection. (Of course, other code could concurrently be making
            # nodes or allowing them to be destroyed, but if so, this test is
            # already very unreliable, as detailed in the method docstring.)
            count = self.impl.count_instances()
            self.assertEqual(count, 9106)

        del head4, head5

        with self.subTest('after deleting local variables head4 and head5'):
            testing.collect_if_not_ref_counting()
            count = self.impl.count_instances()
            self.assertEqual(count, 6)

        head3 = head1

        with self.subTest('after rebinding the head3 local variable'):
            testing.collect_if_not_ref_counting()
            count = self.impl.count_instances()
            self.assertEqual(count, 5)

        del head1

        with self.subTest('after deleting local variable head1'):
            testing.collect_if_not_ref_counting()  # To show no effect.
            count = self.impl.count_instances()
            self.assertEqual(count, 5)

        del head3

        with self.subTest('after deleting local variable head3'):
            testing.collect_if_not_ref_counting()
            count = self.impl.count_instances()
            self.assertEqual(count, 4)

        del head2

        with self.subTest('after deleting local variable head2'):
            testing.collect_if_not_ref_counting()
            count = self.impl.count_instances()
            self.assertEqual(count, 0)

    @unittest.skip("The implementation does not break heterogeneous cycles.")
    def test_single_simple_heterogeneous_cycle_does_not_leak(self):
        """

        """
        class Element:
            pass

        element = Element()
        element.node = sll.Node(element)
        observer = weakref.ref(element)
        del element
        gc.collect()
        self.assertIsNone(observer())

    @unittest.skip("The implementation does not break heterogeneous cycles.")
    def test_nontrivial_heterogeneous_cycles_do_not_leak(self):
        class Element:
            pass

        e1 = Element()
        e2 = Element()
        e3 = Element()
        e4 = Element()

        head = sll.Node.from_iterable([e1, e2, e3, e4])

        e1.n1 = e2.n1 = e3.n1 = e4.n1 = head
        e1.n2 = e2.n2 = e3.n2 = e4.n2 = head.next_node
        e1.n3 = e2.n3 = e3.n3 = e4.n3 = head.next_node.next_node
        e1.n4 = e2.n4 = e3.n4 = e4.n4 = head.next_node.next_node.next_node

        r1 = weakref.ref(e1)
        r2 = weakref.ref(e2)
        r3 = weakref.ref(e3)
        r4 = weakref.ref(e4)

        del e1, e2, e3, e4, head
        gc.collect()

        for name, ref in ('r1', r1), ('r2', r2), ('r3', r3), ('r4', r4):
            with self.subTest(observer=name):
                self.assertIsNone(ref())

    def test_draw_returns_graphviz_digraph(self):
        """
        The draw method returns a graphviz.Digraph instance.

        This doesn't check that anything about the generated graph drawing is
        correct, only that an object of the correct type is returned. The draw
        method must be manually tested in sll.ipynb. Those visualizations also
        serve as a further check that nodes are always reused (where possible),
        and they allow the effects of garbage collection to be observed.
        """
        # Make a few nodes. The draw method should return a graphviz.Digraph
        # even if no nodes exist; then the graph has no nodes or edges. But
        # having nodes and edges (next_node references) may speed up detecting
        # regressions that raise exceptions even in simple cases. _head1 and
        # _head2 hold references and are deliberately never read (hence F841).
        _head1 = sll.Node('a', sll.Node('c'))  # noqa: F841
        _head2 = sll.Node('b', sll.Node('c'))  # noqa: F841

        graph = sll.Node.draw()
        self.assertIsInstance(graph, graphviz.Digraph)


class TestNode(_TestNodeBase, unittest.TestCase):
    """Tests of the sll.Node class."""

    @property
    def impl(self):
        return sll.Node

    def test_class_is_not_TypeNode_subclass(self):
        """The Node class is not a direct or indirect subclass of TypedNode."""
        self.assertFalse(issubclass(sll.Node, sll.TypedNode))

    def test_is_not_TypedNode(self):
        """Node instances are not direct or indirect instances of TypedNode."""
        head = sll.Node('foo')
        self.assertNotIsInstance(head, sll.TypedNode)

    def test_cannot_construct_with_TypedNode_as_second_arg(self):
        """
        It would be especially bad if a Node's next_node could be a TypedNode.

        This is like test_cannot_construct_with_second_arg_not_of_node_type,
        but testing what would be a particularly nasty case. This test does not
        intend to specify any additional restrictions on behavior other than
        those implied by that test taken together with test_is_not_TypedNode.
        In particular, no special check for TypedNode is needed in Node; the
        goal is to catch uses that are accidentally wrong, not intentionally
        weird and broken code such as having a class inherit from (and/or be
        registered as a virtual subclass of) both Node and TypedNode.
        """
        with self.assertRaises(TypeError):
            sll.Node('foo', sll.TypedNode('bar'))

    def test_repr_shows_no_next_node_if_none(self):
        head = sll.Node('foo')
        self.assertEqual(repr(head), "Node('foo')")

    def test_repr_shows_chain_recursively(self):
        expected = "Node('a', Node('b', Node('c', Node('d'))))"
        head = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        self.assertEqual(repr(head), expected)

    def test_nodes_holding_cross_type_same_value_no_next_are_equal(self):
        lhs = sll.Node(10)
        rhs = sll.Node(10.0)
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_cross_type_same_value_no_next_are_identical(self):
        lhs = sll.Node(10)
        rhs = sll.Node(10.0)
        self.assertIs(lhs, rhs)

    def test_nodes_heading_cross_type_same_value_chains_are_equal(self):
        lhs = sll.Node(False, sll.Node(1, sll.Node(2.0, sll.Node(3))))
        rhs = sll.Node(0, sll.Node(True, sll.Node(2, sll.Node(3.0))))
        self.assertEqual(lhs, rhs)

    def test_nodes_heading_cross_type_same_value_chains_are_identical(self):
        lhs = sll.Node(False, sll.Node(1, sll.Node(2.0, sll.Node(3))))
        rhs = sll.Node(0, sll.Node(True, sll.Node(2, sll.Node(3.0))))
        self.assertIs(lhs, rhs)


class TestTypedNode(_TestNodeBase, unittest.TestCase):
    """Tests of the sll.TypedNode class."""

    @property
    def impl(self):
        return sll.TypedNode

    def test_class_is_not_Node_subclass(self):
        """The TypedNode class is not a direct or indirect subclass of Node."""
        self.assertFalse(issubclass(sll.TypedNode, sll.Node))

    def test_is_not_Node(self):
        """TypedNode instances are not direct or indirect instances of Node."""
        head = sll.TypedNode('foo')
        self.assertNotIsInstance(head, sll.Node)

    def test_cannot_construct_with_Node_as_second_arg(self):
        """
        It would be especially bad if a TypedNode's next_node could be a Node.

        This is like test_cannot_construct_with_second_arg_not_of_node_type,
        but testing what would be a particularly nasty case. This test does not
        intend to specify any additional restrictions on behavior other than
        those implied by that test taken together with test_is_not_Node. See
        TestNode.test_cannot_construct_with_TypedNode_as_second_arg about this.
        """
        with self.assertRaises(TypeError):
            sll.TypedNode('foo', sll.Node('bar'))

    def test_repr_shows_no_next_node_if_none(self):
        head = sll.TypedNode('foo')
        self.assertEqual(repr(head), "TypedNode('foo')")

    def test_repr_shows_chain_recursively(self):
        expected = (
            "TypedNode('a', TypedNode('b', TypedNode('c', TypedNode('d'))))")
        head = sll.TypedNode(
            'a', sll.TypedNode('b', sll.TypedNode('c', sll.TypedNode('d'))))
        self.assertEqual(repr(head), expected)

    def test_nodes_holding_cross_type_same_value_no_next_are_not_equal(self):
        lhs = sll.TypedNode(10)
        rhs = sll.TypedNode(10.0)
        self.assertNotEqual(lhs, rhs)

    def test_nodes_holding_cross_type_same_value_no_next_are_not_identical(
            self):
        lhs = sll.TypedNode(10)
        rhs = sll.TypedNode(10.0)
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_cross_type_same_value_chains_are_not_equal(self):
        lhs = sll.TypedNode(
            False, sll.TypedNode(1, sll.TypedNode(2.0, sll.TypedNode(3))))
        rhs = sll.TypedNode(
            0, sll.TypedNode(True, sll.TypedNode(2, sll.TypedNode(3.0))))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_cross_type_same_value_chains_are_not_identical(
            self):
        lhs = sll.TypedNode(
            False, sll.TypedNode(1, sll.TypedNode(2.0, sll.TypedNode(3))))
        rhs = sll.TypedNode(
            0, sll.TypedNode(True, sll.TypedNode(2, sll.TypedNode(3.0))))
        self.assertIsNot(lhs, rhs)


def _fake(value, next_node=None):
    """
    Create a SimpleNamespace to use as a singly linked list node for testing.

    Such an object, with appropriate attributes and used in an appropriate way,
    as we are, really is an SLL node. This is a "fake" in the sense specific to
    unit testing. See https://martinfowler.com/articles/mocksArentStubs.html.
    (Though if we were to regard it as a double for a hash-consed node, rather
    than just any singly linked list node, then it would be closer to a stub.)

    >>> _fake('a', _fake('b'))
    namespace(value='a', next_node=namespace(value='b', next_node=None))
    >>> _fake.from_iterable('ab')
    namespace(value='a', next_node=namespace(value='b', next_node=None))
    """
    return types.SimpleNamespace(value=value, next_node=next_node)


def _from_iterable(values):
    """
    Create an SLL of the given values with SimpleNamespace instances as nodes.

    This facilitates fake.from_iterable, and takes advantage of SimpleNamespace
    being mutable to use an algorithm that cannot be used for immutable nodes
    such as sll.Node. This avoids duplicating logic, and possibly bugs, across
    both code and tests.
    """
    sentinel = _fake('arbitrary')
    pre = sentinel

    for value in values:
        pre.next_node = _fake(value)
        pre = pre.next_node

    return sentinel.next_node


_fake.from_iterable = _from_iterable


class TestTraverse(unittest.TestCase):
    """
    Tests for the sll.traverse function.

    This includes tests using a test double for the nodes, as well as on singly
    linked lists formed as chains of sll.Node instances.
    """

    _parameterize_by_node_type = parameterized.expand([
        ('SimpleNamespace', _fake),
        (sll.Node.__name__, sll.Node),
        (sll.TypedNode.__name__, sll.TypedNode),
    ])
    """Parameterize a test method by choice of SLL-node factory."""

    def test_empty_chain_yields_nothing(self):
        it = sll.traverse(None)
        with self.assertRaises(StopIteration):
            next(it)

    @_parameterize_by_node_type
    def test_nonempty_chain_yields_values_front_to_back(self, _name, factory):
        head = factory(1, factory(5, factory(2, factory(4, factory(3)))))
        result = sll.traverse(head)
        self.assertListEqual(list(result), [1, 5, 2, 4, 3])

    def test_traversal_is_lazy(self):
        expected = [4, 5, 6, 7, 8, 9] * 5
        head = _fake(4, _fake(5, _fake(6, _fake(7, _fake(8, _fake(9))))))
        head.next_node.next_node.next_node.next_node.next_node.next_node = head
        result = sll.traverse(head)
        prefix = itertools.islice(result, 30)
        self.assertListEqual(list(prefix), expected)

    @_parameterize_by_node_type
    def test_long_chains_are_supported(self, _name, factory):
        expected = list(range(9000))
        head = factory.from_iterable(range(9000))
        result = sll.traverse(head)
        self.assertListEqual(list(result), expected)


if __name__ == '__main__':
    unittest.main()
