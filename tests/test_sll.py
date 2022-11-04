#!/usr/bin/env python

"""
Tests for sll.py.

See also test_sll.txt for extended versions of the doctests in sll.py.

One reasonable general approach for implementing sll.HashNode is to:

1. In any order, get all TestHashNodeBasic, TestHashNodePathologicalEquality,
   and TestTraverse unittest tests to pass, as well as all doctests in sll.py
   and test_sll.txt, and make sure HashNode.draw works by testing it in
   sll.ipynb and carefully inspecting the output.

   An implementation that only passes those tests is a useful starting point
   for tackling the important but subtler issues the other tests raise.

2. Get the TestHashNodeHeterogeneousCycles unittest tests to pass. Ensure that
   this does not cause any previously passing tests, mentioned above, to fail.

3. Observe how resurrection can circumvent the uniqueness guarantee. It is not
   a goal to prevent this, only to understand it and to check it is clearly
   documented. Currently the code to help demonstrate this is in sll_wip.ipynb.

4. Get the _CachedEq doctests, TestHashNodeReentrantCachedEq unittest tests,
   and TestHashNodeReentrantDevious unittest tests to pass.
"""

import functools
import gc
import itertools
import math
import types
import unittest
import weakref

import graphviz
from parameterized import parameterized

from algoviz import sll, testing

_TEST_FOR_HETEROGENEOUS_CYCLE_LEAKAGE = True
"""
Whether the tests in the TestHashNodeHeterogeneousCycles class will be run.

Heterogeneous cycles should not leak, so this should be set to True. But it may
sometimes be useful to suppress these tests temporarily, during development.
"""


class TestHashNodeBasic(unittest.TestCase):
    """Tests for basic sll.HashNode functionality."""

    def test_cannot_construct_with_zero_args(self):
        with self.assertRaises(TypeError):
            sll.HashNode()

    def test_can_construct_with_one_arg(self):
        head = sll.HashNode('foo')
        self.assertIsInstance(head, sll.HashNode)

    def test_constructing_with_one_arg_has_value(self):
        head = sll.HashNode('foo')
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_one_arg_has_no_next_node(self):
        head = sll.HashNode('foo')
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
            sll.HashNode('foo', object())

    def test_can_construct_with_two_args_second_none(self):
        head = sll.HashNode('foo', None)
        self.assertIsInstance(head, sll.HashNode)

    def test_constructing_with_two_args_second_none_has_value(self):
        head = sll.HashNode('foo', None)
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_two_args_second_none_has_no_next_node(self):
        head = sll.HashNode('foo', None)
        self.assertIsNone(head.next_node)

    def test_can_construct_with_two_args_second_node(self):
        head = sll.HashNode('foo', sll.HashNode('bar'))
        self.assertIsInstance(head, sll.HashNode)

    def test_constructing_with_two_args_second_node_has_value(self):
        head = sll.HashNode('foo', sll.HashNode('bar'))
        self.assertEqual(head.value, 'foo')

    def test_constructing_with_two_args_second_node_has_it_as_next_node(self):
        next_node = sll.HashNode('bar')
        head = sll.HashNode('foo', next_node)
        self.assertIs(head.next_node, next_node)

    def test_value_attribute_is_read_only(self):
        """The value attribute cannot be written."""
        head = sll.HashNode('foo')
        with self.assertRaises(AttributeError):
            head.value = 'bar'

    def test_value_attribute_cannot_be_deleted(self):
        head = sll.HashNode('foo')
        with self.assertRaises(AttributeError):
            del head.value

    def test_next_node_attribute_is_read_only_if_none(self):
        """The next_node attribute cannot be written."""
        head = sll.HashNode('foo')
        with self.assertRaises(AttributeError):
            head.next_node = sll.HashNode('baz')

    def test_next_node_attribute_is_read_only_if_not_none(self):
        """The next_node attribute cannot be written."""
        head = sll.HashNode('foo', sll.HashNode('bar'))
        with self.assertRaises(AttributeError):
            head.next_node = sll.HashNode('baz')

    def test_next_node_attribute_cannot_be_deleted_if_none(self):
        head = sll.HashNode('foo')
        with self.assertRaises(AttributeError):
            del head.next_node

    def test_next_node_attribute_cannot_be_deleted_if_not_none(self):
        head = sll.HashNode('foo', sll.HashNode('bar'))
        with self.assertRaises(AttributeError):
            del head.next_node

    def test_new_attributes_cannot_be_created(self):
        head = sll.HashNode('foo')
        with self.assertRaises(AttributeError):
            head.new_attribute_created_pursuant_to_my_whims = 'oof'

    def test_no_instance_dictionary(self):
        """
        Instances should have no __dict__, for a low memory footprint.

        This is a separate requirement from not creating new attributes. Often
        __slots__ is used as a way to achieve that without the complexity of
        overriding __setattr__ and modifying the code to accommodate its
        overridden logic. But sometimes our primary goal really is to use less
        memory (or, occasionally, to access attributes faster even aside from
        the speed benefits of lower memory usage). Node classes in linked data
        structures are a case where this is desirable, since, in many uses, a
        very large number of nodes may be created.
        """
        head = sll.HashNode('foo')
        with self.assertRaises(AttributeError):
            head.__dict__

    def test_no_finalizer(self):
        """
        The class should have no __del__ method.

        The vast majority of classes should have no __del__ method, but for a
        node class, the performance implications make it even less likely that
        it could be reasonable to have one: __del__ can resurrect objects, so a
        garbage collector will (at least sometimes) need to defer collecting
        them until it has traversed the object graph *again* to check for this.

        This requirement shouldn't be relaxed without benchmarking (including
        of peak memory usage with and without __del__). But also, it is very
        unlikely __del__ would help HashNode. The real reason for this test is
        to avert confusion about how nondeterministic cleanup should be done.

        In contrast to __del__ methods, weak reference callbacks, including
        weakref.finalize, are not prohibited. But, if at all possible, any use
        of them in sll.HashNode should be via even higher level facilities.
        """
        with self.assertRaises(AttributeError):
            sll.HashNode.__del__

    def test_repr_shows_no_next_node_if_none(self):
        head = sll.HashNode('foo')
        self.assertEqual(repr(head), "HashNode('foo')")

    def test_repr_shows_chain_recursively(self):
        expected = "HashNode('a', HashNode('b', HashNode('c', HashNode('d'))))"
        head = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        self.assertEqual(repr(head), expected)

    @parameterized.expand([
        ('one', 1),
        ('zero', 0),
        ('obj', object()),
        ('none', None),
    ])
    def test_is_truthy(self, _name, value):
        head = sll.HashNode(value)
        self.assertTrue(head)

    def test_nodes_holding_same_type_value_no_next_are_equal(self):
        lhs = sll.HashNode('foo')
        rhs = sll.HashNode('foo')
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_same_type_value_no_next_are_identical(self):
        lhs = sll.HashNode('foo')
        rhs = sll.HashNode('foo')
        self.assertIs(lhs, rhs)

    def test_nodes_holding_same_type_value_next_are_equal(self):
        lhs = sll.HashNode('foo', sll.HashNode('bar'))
        rhs = sll.HashNode('foo', sll.HashNode('bar'))
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_same_type_value_next_are_identical(self):
        lhs = sll.HashNode('foo', sll.HashNode('bar'))
        rhs = sll.HashNode('foo', sll.HashNode('bar'))
        self.assertIs(lhs, rhs)

    def test_nodes_heading_same_type_value_chain_are_equal(self):
        lhs = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        rhs = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        self.assertEqual(lhs, rhs)

    def test_nodes_heading_same_type_value_chain_are_identical(self):
        lhs = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        rhs = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        self.assertIs(lhs, rhs)

    def test_nodes_holding_cross_type_same_value_no_next_are_equal(self):
        lhs = sll.HashNode(10)
        rhs = sll.HashNode(10.0)
        self.assertEqual(lhs, rhs)

    def test_nodes_holding_cross_type_same_value_no_next_are_identical(self):
        lhs = sll.HashNode(10)
        rhs = sll.HashNode(10.0)
        self.assertIs(lhs, rhs)

    def test_nodes_heading_cross_type_same_value_chains_are_equal(self):
        lhs = sll.HashNode(
            False, sll.HashNode(1, sll.HashNode(2.0, sll.HashNode(3))))
        rhs = sll.HashNode(
            0, sll.HashNode(True, sll.HashNode(2, sll.HashNode(3.0))))
        self.assertEqual(lhs, rhs)

    def test_nodes_heading_cross_type_same_value_chains_are_identical(self):
        lhs = sll.HashNode(
            False, sll.HashNode(1, sll.HashNode(2.0, sll.HashNode(3))))
        rhs = sll.HashNode(
            0, sll.HashNode(True, sll.HashNode(2, sll.HashNode(3.0))))
        self.assertIs(lhs, rhs)

    def test_nodes_heading_different_values_no_next_are_not_equal(self):
        lhs = sll.HashNode('foo')
        rhs = sll.HashNode('bar')
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_different_values_no_next_are_not_identical(self):
        lhs = sll.HashNode('foo')
        rhs = sll.HashNode('bar')
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_different_values_same_next_are_not_equal(self):
        lhs = sll.HashNode('foo', sll.HashNode('baz'))
        rhs = sll.HashNode('bar', sll.HashNode('baz'))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_different_values_same_next_are_not_identical(self):
        lhs = sll.HashNode('foo', sll.HashNode('baz'))
        rhs = sll.HashNode('bar', sll.HashNode('baz'))
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_same_values_different_next_are_not_equal(self):
        lhs = sll.HashNode('foo', sll.HashNode('bar'))
        rhs = sll.HashNode('foo', sll.HashNode('baz'))
        self.assertNotEqual(lhs, rhs)

    def test_nodes_heading_same_values_different_next_are_not_identical(self):
        lhs = sll.HashNode('foo', sll.HashNode('bar'))
        rhs = sll.HashNode('foo', sll.HashNode('baz'))
        self.assertIsNot(lhs, rhs)

    def test_nodes_heading_different_length_chains_are_not_equal(self):
        shorter = sll.HashNode('foo')
        longer = sll.HashNode('foo', sll.HashNode('bar'))
        with self.subTest(lhs='shorter', rhs='longer'):
            self.assertNotEqual(shorter, longer)
        with self.subTest(lhs='longer', rhs='shorter'):
            self.assertNotEqual(longer, shorter)

    def test_nodes_heading_different_length_chains_are_not_identical(self):
        shorter = sll.HashNode('foo')
        longer = sll.HashNode('foo', sll.HashNode('bar'))
        with self.subTest(lhs='shorter', rhs='longer'):
            self.assertIsNot(shorter, longer)
        with self.subTest(lhs='longer', rhs='shorter'):
            self.assertIsNot(longer, shorter)

    def test_matches_keyword_class_pattern(self):
        match sll.HashNode(10, sll.HashNode(20, sll.HashNode(30))):
            case sll.HashNode(next_node=sll.HashNode(
                    value=20,
                    next_node=sll.HashNode(next_node=None) as node)):
                self.assertIs(node, sll.HashNode(30))
            case _:
                self.fail('head did not match the keyword pattern')

    def test_matches_positional_class_pattern(self):
        match sll.HashNode(10, sll.HashNode(20, sll.HashNode(30))):
            case sll.HashNode(
                    _, sll.HashNode(20, sll.HashNode(_, None) as node)):
                self.assertIs(node, sll.HashNode(30))
            case _:
                self.fail('head did not match the positional pattern')

    def test_from_iterable_returns_none_from_empty_sequence(self):
        head = sll.HashNode.from_iterable([])
        self.assertIsNone(head)

    def test_from_iterable_returns_none_from_empty_iterator(self):
        head = sll.HashNode.from_iterable(iter([]))
        self.assertIsNone(head)

    def test_from_iterable_finds_chain_from_nonempty_sequence(self):
        # NOTE: This test MUST be written to assign "expected" first.
        expected = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        actual = sll.HashNode.from_iterable('abcd')
        self.assertIs(actual, expected)

    def test_from_iterable_builds_chain_from_nonempty_sequence(self):
        # NOTE: This test MUST be written to assign "actual" first.
        actual = sll.HashNode.from_iterable('abcd')
        expected = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        self.assertIs(actual, expected)

    def test_from_iterable_builds_long_chain(self):
        head = sll.HashNode.from_iterable(range(9000))
        self.assertIsInstance(head, sll.HashNode)

    def test_from_iterable_long_chain_has_same_length_as_input(self):
        head = sll.HashNode.from_iterable(range(9000))

        length = 0
        node = head
        while node:
            length += 1
            node = node.next_node

        self.assertEqual(length, 9000)

    def test_from_iterable_long_chain_has_equal_values_to_input(self):
        head = sll.HashNode.from_iterable(range(9000))

        values = []
        node = head
        while node:
            values.append(node.value)
            node = node.next_node

        self.assertListEqual(values, list(range(9000)))

    def test_from_iterable_new_longer_chain_can_overlap_long_chain(self):
        shorter = sll.HashNode.from_iterable(range(9000))
        longer = sll.HashNode.from_iterable(range(-100, 9000))

        node = longer
        for _ in range(100):
            node = node.next_node

        self.assertIs(node, shorter)

    def test_from_iterable_new_shorter_chain_can_overlap_long_chain(self):
        longer = sll.HashNode.from_iterable(range(-100, 9000))
        shorter = sll.HashNode.from_iterable(range(9000))

        node = longer
        for _ in range(100):
            node = node.next_node

        self.assertIs(node, shorter)

    @parameterized.expand(['__eq__', '__ne__', '__hash__'])
    def test_type_uses_reference_equality_comparison(self, name):
        expected = getattr(object, name)
        actual = getattr(sll.HashNode, name)
        self.assertIs(actual, expected)

    def test_no_more_nodes_are_maintained_than_necessary(self):
        """
        Nodes are always shared and allowed to be collected when unreachable.

        To a greater extent than other tests in this test class, these tests
        assume no other code in the same test runner process has created and
        *kept* references to HashNode instances. Unless some other code in the
        project does so and is under test, this is unlikely to be a problem.

        Note also that these tests rely on the count_instances method being
        correctly implemented. But it is fairly unlikely that an unintentional
        bug in that method would cause all tests to wrongly pass.

        This method does not cover the tricky issue of heterogeneous cycles.
        Those tests are in the TestHashNodeHeterogeneousCycles class (below).
        """
        head1 = sll.HashNode(
            'a', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        head2 = sll.HashNode(
            'x', sll.HashNode('b', sll.HashNode('c', sll.HashNode('d'))))
        head3 = sll.HashNode(0)
        head4 = sll.HashNode.from_iterable(range(9000))

        with self.subTest('before any of head1-head5 are collectable'):
            testing.collect_if_not_ref_counting()
            self.assertEqual(sll.HashNode.count_instances(), 9006)

        head5 = sll.HashNode.from_iterable(range(-100, 9000))

        with self.subTest('after creating head5'):
            # We do not need to force a collection here regardless of platform,
            # since we have only created nodes since the last possibly forced
            # collection. (Of course, other code could concurrently be making
            # nodes or allowing them to be destroyed, but if so, this test is
            # already very unreliable, as detailed in the method docstring.)
            count = sll.HashNode.count_instances()
            self.assertEqual(count, 9106)

        del head4, head5

        with self.subTest('after deleting local variables head4 and head5'):
            testing.collect_if_not_ref_counting()
            count = sll.HashNode.count_instances()
            self.assertEqual(count, 6)

        head3 = head1

        with self.subTest('after rebinding the head3 local variable'):
            testing.collect_if_not_ref_counting()
            count = sll.HashNode.count_instances()
            self.assertEqual(count, 5)

        del head1

        with self.subTest('after deleting local variable head1'):
            testing.collect_if_not_ref_counting()  # To show no effect.
            count = sll.HashNode.count_instances()
            self.assertEqual(count, 5)

        del head3

        with self.subTest('after deleting local variable head3'):
            testing.collect_if_not_ref_counting()
            count = sll.HashNode.count_instances()
            self.assertEqual(count, 4)

        del head2

        with self.subTest('after deleting local variable head2'):
            testing.collect_if_not_ref_counting()
            count = sll.HashNode.count_instances()
            self.assertEqual(count, 0)

    def test_draw_returns_graphviz_digraph(self):
        """
        The draw method returns a graphviz.Digraph instance.

        This doesn't check that anything about the generated graph drawing is
        correct, only that an object of the correct type is returned. The draw
        method must be manually tested in sll.ipynb. Those visualizations also
        serve as a further check that nodes are always reused as required, and
        they allow the effects of garbage collection to be observed.
        """
        # Make a few nodes. The draw method should return a graphviz.Digraph
        # even if no nodes exist; then the graph has no nodes or edges. But
        # having nodes and edges (next_node references) may speed up detecting
        # regressions that raise exceptions even in simple cases. _head1 and
        # _head2 keep nodes alive and are deliberately never read, so we
        # suppress flake8's "local variable ... is assigned to but never used".
        _head1 = sll.HashNode('a', sll.HashNode('c'))  # noqa: F841
        _head2 = sll.HashNode('b', sll.HashNode('c'))  # noqa: F841

        graph = sll.HashNode.draw()
        self.assertIsInstance(graph, graphviz.Digraph)


def _subtest_by_nanlike(func):
    """Sub-test separate NaN or NaN-like objects."""
    @functools.wraps(func)
    def wrapped(self):
        nan_parameters = [
            ('math.nan', math.nan),
            ('math.inf - math.inf', math.inf - math.inf),
        ]

        for expr, nan in nan_parameters:
            with self.subTest(expr):
                # Check that nan is non-self-equal. This is per subtest and not
                # done eagerly, which would keep the module from loading and
                # give an error that didn't clarify what tests were affected.
                if nan == nan:
                    raise Exception(
                        "platform has non-pathological NaN, can't test")

                # Run the actual test, with this NaN object.
                func(self, nan)

        with self.subTest('testing.NonSelfEqual()'):
            pathological_non_nan = testing.NonSelfEqual()

            if pathological_non_nan == pathological_non_nan:
                raise Exception('bug in testing.NonSelfEqual test helper')

            # Run the actual test, with this similarly pathological object.
            func(self, pathological_non_nan)

    return wrapped


def _subtest_by_nonidentical_nanlike_pair(func):
    """Sub-test separate pairs of related nonidentical NaN/NaN-like objects."""
    @functools.wraps(func)
    def wrapped(self):
        parameters = [
            ('NaN',
                math.nan,
                math.inf - math.inf,
                'very weird (broken?) floating point NaN equality'),

            ('non-NaN pathological',
                testing.NonSelfEqual(),
                testing.NonSelfEqual(),
                'bug in testing.NonSelfEqual test helper'),
        ]

        for name, lhs_obj, rhs_obj, error_message in parameters:
            with self.subTest(name):
                # Check that they are not equal, erroring out if they are.
                if lhs_obj == rhs_obj:
                    raise Exception(error_message)

                # Proceed with the core test logic.
                func(self, lhs_obj, rhs_obj)

    return wrapped


class TestHashNodePathologicalEquality(unittest.TestCase):
    """Tests that sll.HashNode properly handles non-self-equal elements."""

    @_subtest_by_nanlike
    def test_nodes_holding_same_nanlike_no_next_are_equal(self, obj):
        lhs = sll.HashNode(obj)
        rhs = sll.HashNode(obj)
        self.assertEqual(lhs, rhs)

    @_subtest_by_nanlike
    def test_nodes_holding_same_nanlike_no_next_are_identical(self, obj):
        lhs = sll.HashNode(obj)
        rhs = sll.HashNode(obj)
        self.assertIs(lhs, rhs)

    @_subtest_by_nanlike
    def test_nodes_holding_same_nanlike_different_next_are_not_equal(self,
                                                                     obj):
        lhs = sll.HashNode(obj, sll.HashNode('foo'))
        rhs = sll.HashNode(obj, sll.HashNode('bar'))
        self.assertNotEqual(lhs, rhs)

    @_subtest_by_nanlike
    def test_nodes_holding_same_nanlike_different_next_are_not_identical(self,
                                                                         obj):
        lhs = sll.HashNode(obj, sll.HashNode('foo'))
        rhs = sll.HashNode(obj, sll.HashNode('bar'))
        self.assertIsNot(lhs, rhs)

    @_subtest_by_nonidentical_nanlike_pair
    def test_nodes_holding_different_nanlike_no_next_are_not_equal(
            self, lhs_obj, rhs_obj):
        lhs = sll.HashNode(lhs_obj)
        rhs = sll.HashNode(rhs_obj)
        self.assertNotEqual(lhs, rhs)

    @_subtest_by_nonidentical_nanlike_pair
    def test_nodes_holding_different_nanlike_no_next_are_not_identical(
            self, lhs_obj, rhs_obj):
        lhs = sll.HashNode(lhs_obj)
        rhs = sll.HashNode(rhs_obj)
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
    such as sll.HashNode. This avoids duplicating logic, and possibly bugs,
    across both code and tests.
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
    linked lists formed as chains of sll.HashNode instances.
    """

    _parameterize_by_node_type = parameterized.expand([
        ('SimpleNamespace', _fake),
        (sll.HashNode.__name__, sll.HashNode),
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


@unittest.skipUnless(_TEST_FOR_HETEROGENEOUS_CYCLE_LEAKAGE,
                     "It may help to get the more basic tests passing first.")
class TestHashNodeHeterogeneousCycles(unittest.TestCase):
    """
    Tests to check that sll.HashNode does not leak heterogeneous cycles.

    In a homogeneous cycle of sll.HashNode objects, following nodes' next_node
    attributes, and/or their value attributes in the case of nested SLLs (where
    elements are also nodes), would lead to a node already seen. sll.HashNode
    is immutable. So homogeneous cycles of sll.HashNode objects do not form
    (unless client code violates encapsulation). No matter how many linked
    lists a node is shared between, and no matter how deeply those linked lists
    are nested by having nodes appear not just as successors but also as
    elements, there is no potential to create cycles or leak nodes.

    Heterogeneous cycles are another story. An object can be immutable, in that
    its value never changes, yet still hold mutable state that doesn't affect
    its value. It's reasonable for such an object to be hashable. Most classes
    work this way, inheriting __eq__ and __hash__ from object but allowing
    arbitrary attributes in their instance dictionaries. So we wouldn't want to
    prohibit most such objects as elements. But what if a node's element comes
    to have an attribute that doesn't participate in equality comparison or
    hashing but refers, directly or indirectly, back to the node itself?

    That is a heterogenous cycle: part of the cycle is through an object of an
    unrelated type. Our private table that looks up nodes by their elements and
    successors holds weak references to the nodes it returns, so it doesn't
    prevent them from being garbage collected. But the elements and successors
    are held by strong references. That's normally no problem: as long as a
    node exists, it keeps its element and successor alive anyway, and when a
    node is destroyed, the table takes care of removing the entry for it (using
    weakref callbacks). But if there is a chain of strong references from the
    element back to the node, then the table holds a strong reference to the
    element, which holds a strong reference to the node. Then the node, being
    reachable, can't be garbage collected. Unless the heterogeneous cycle is
    somehow broken, the entry is never removed from the table, since it would
    only be removed when the node it keeps reachable becomes unreachable and is
    collected, which its presence ensures cannot happen.

    Note that this is NOT related to the limitations of reference counting. We
    assume a cyclic garbage collector is available. The problem arises when the
    table holds a strong reference into a heterogeneous cycle.
    """

    def test_single_simple_heterogeneous_cycle_does_not_leak(self):
        """An element can refer to its own node, with no leak."""
        class Element:
            pass

        element = Element()
        element.node = sll.HashNode(element)
        observer = weakref.ref(element)
        del element
        gc.collect()
        self.assertIsNone(observer())

    def test_nontrivial_heterogeneous_cycles_do_not_leak(self):
        """All elements of one chain can refer to all nodes, with no leak."""
        class Element:
            pass

        e1 = Element()
        e2 = Element()
        e3 = Element()
        e4 = Element()

        head = sll.HashNode.from_iterable([e1, e2, e3, e4])

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

    def test_many_heterogeneous_cycles_do_not_leak(self):
        """All overlapping SLLs' elements can reach all nodes, with no leak."""
        class Element:
            def __init__(self, value, aux):
                self._value = value
                self._aux = aux

            def __repr__(self):
                return '<{} at 0x{:X}, value={!r}, aux at 0x{:X}>'.format(
                    type(self).__name, id(self), self._value, id(self._aux))

            def __eq__(self, other):
                if isinstance(other, type(self)):
                    return self._value == other._value
                return NotImplemented

            def __hash__(self):
                return hash(self._value)

        N = 100
        layers = []
        top_layer = [None] * N
        for _ in range(N):
            top_layer = [sll.HashNode(Element(j, layers), tail)
                         for j, tail in enumerate(top_layer)]
            layers.append(top_layer)

        testing.collect_if_not_ref_counting()
        if sll.HashNode.count_instances() != N**2:
            raise Exception('failed to arrange the heterogeneous cycles')

        del layers, top_layer
        gc.collect()
        self.assertEqual(sll.HashNode.count_instances(), 0)

    def test_highly_redundant_heterogeneous_cycles_do_not_leak(self):
        """
        All overlapping SLLs' elements can refer to all nodes, with no leak.

        This is like test_many_heterogeneous_cycles_do_not_leak, but with no
        choke point: instead of all nodes referring to the same list object
        that can reach all nodes, they refer to separate lists of all nodes.
        This should not make an important difference--it would be strange if
        either if one of these two tests passed and the other failed--but it
        might confer greater confidence that leaks are prevented in general.
        """
        class Element:
            def __init__(self, value):
                self._value = value
                self.aux = []

            def __repr__(self):
                return '<{} at 0x{:X}, value={!r}, len(aux)={}>'.format(
                    type(self).__name, id(self), self._value, len(self._aux))

            def __eq__(self, other):
                if isinstance(other, type(self)):
                    return self._value == other._value
                return NotImplemented

            def __hash__(self):
                return hash(self._value)

        N = 20
        layers = []
        top_layer = [None] * N
        for _ in range(N):
            top_layer = [sll.HashNode(Element(j), tail)
                         for j, tail in enumerate(top_layer)]
            layers.append(top_layer)

        nodes = list(itertools.chain.from_iterable(layers))
        for node in nodes:
            node.value.aux.extend(nodes)

        testing.collect_if_not_ref_counting()
        if sll.HashNode.count_instances() != N**2:
            raise Exception('failed to arrange the heterogeneous cycles')

        del layers, top_layer, nodes, node
        gc.collect()
        self.assertEqual(sll.HashNode.count_instances(), 0)

    def test_homogeneous_cycles_of_elements_do_not_leak(self):
        """
        All elements can refer to each other, with no leak.

        As detailed in this test class's docstring, we can't have cycles of all
        sll.HashNode objects. But we may, of course, have cycles of elements,
        where the (strong) references that form the cycle are between elements
        rather than nodes. There is no problem with this and no reason to think
        this wouldn't work, and this test method exists more to document the
        distinction than to safeguard against anything. If all the tests in
        TestHashNodeBasic pass, this test should also pass.
        """
        class Element:
            pass

        e1 = Element()
        e2 = Element()
        e3 = Element()
        e4 = Element()

        head = sll.HashNode.from_iterable([e1, e2, e3, e4])

        e1.e1 = e2.e1 = e3.e1 = e4.e1 = e1
        e1.e2 = e2.e2 = e3.e2 = e4.e2 = e2
        e1.e3 = e2.e3 = e3.e3 = e4.e3 = e3
        e1.e4 = e2.e4 = e3.e4 = e4.e4 = e4

        r1 = weakref.ref(e1)
        r2 = weakref.ref(e2)
        r3 = weakref.ref(e3)
        r4 = weakref.ref(e4)

        del e1, e2, e3, e4, head
        gc.collect()

        for name, ref in ('r1', r1), ('r2', r2), ('r3', r3), ('r4', r4):
            with self.subTest(observer=name):
                self.assertIsNone(ref())


class _CachedEq:
    """
    Class to try to deadlock a non-reentrant sll.HashNode lock. For testing.

    _CachedEq equality comparison and hashing use the global caching supplied
    by sll.HashNode to speed up subsequent comparisons. This just works:

    >>> x = _CachedEq('reentrant?')
    >>> x
    _CachedEq(['r', 'e', 'e', 'n', 't', 'r', 'a', 'n', 't', '?'])
    >>> hash(x) == hash(x)
    True
    >>> x == _CachedEq('other')
    False
    >>> x == _CachedEq('reentrant?')
    True

    Our _CachedEq instance is hashable, so it can be an sll.HashNode element:

    >>> sll.HashNode(x)
    HashNode(_CachedEq(['r', 'e', 'e', 'n', 't', 'r', 'a', 'n', 't', '?']))

    But if a _CachedEq instance whose SLL is not yet created is stored in an
    sll.HashNode, sll.HashNode.__new__'s act of hashing the _CachedEq object
    causes another sll.HashNode to be created while that "first" sll.HashNode
    object is still being created. This deadlocks if the lock is non-reentrant:

    >>> sll.HashNode(_CachedEq('sabotage'))  # doctest: +SKIP
    HashNode(_CachedEq(['s', 'a', 'b', 'o', 't', 'a', 'g', 'e']))

    Just making the lock reentrant is attractive. On a single thread, the code
    (being synchronous, and pairing acquisition and release) behaves as it
    would without locking. If we didn't need to worry about multiple threads,
    we would likely have written the same code, but without a lock. But would
    that have been right? Do reentrant sll.HashNode calls always behave well?

    Let's consider an approach that makes _CachedEq work without a reentrant
    lock. sll.HashNode(x, n) looks up a key in a table. Calling __hash__ on
    that key causes x.__hash__ to be called. Now suppose _Key is the key type.
    If _Key were to precompute its __hash__ result in _Key.__init__, and if
    sll.HashNode.__new__ were to call _Key once, before taking the lock, then
    sll.HashNode would work with _CachedEq, even if the lock is non-reentrant.

    Implementing _Key reveals the problem with BOTH approaches. The result of
    __hash__ can be precomputed, because it really returns a prehash: a value
    depending only on the key, and not on hash table implementation or bucket
    count. (Remember, a true hash is a bucket index.) But looking up a key uses
    both __hash__ and __eq__. We can't usually precompute all possible results
    of __eq__. We could effectively achieve the goal of precomputing all
    possible results of __eq__ by ensuring that each value is represented by
    only one object at a time and doing identity comparison... except that's
    hash consing, which is what we're trying to implement!

    It's feasible for sll.HashNode to support types like _CachedEq, because
    after __hash__ is called successfully on a _CachedEq instance, __eq__ on
    the same instance never calls sll.HashNode. Other types, intentionally or
    due to bugs, may call sll.HashNode from their __eq__ methods. This would be
    tricky to make safe. After sll.HashNode.__new__(x, n) subscripts a table
    with a key whose __eq__ method calls x.__eq__, doesn't find the key, and
    creates a new node, it subscripts the table again to insert the new node.
    This is a critical time: a node exists that isn't yet in the table. The
    operation of attempting to add it to the table calls x.__eq__ again, which
    could call sll.HashNode(x, n) again.

    Even though this problem is unrelated to threading, a non-reentrant lock
    prevented it. I don't know of a way to make reentering sll.HashNode.__new__
    through an element type's __eq__ safe in Python without greatly increasing
    code complexity. Instead, we can detect it and raise RuntimeError rather
    than deadlocking. We could support reentrance via __hash__ but not __eq__,
    to allow types like _CachedEq to work. Since that isn't a design goal, we
    forgo it for simplicity. sll.HashNode doesn't need to work with _CachedEq;
    the error just needs to be represented by a reasonable exception:

    >>> sll.HashNode(_CachedEq('sabotage'))
    Traceback (most recent call last):
      ...
    RuntimeError: HashNode.__new__ reentered through __hash__ or __eq__
    """

    __slots__ = ('_elements', '_lazy_head')

    _not_computed = object()

    def __init__(self, iterable):
        self._elements = list(iterable)
        self._lazy_head = self._not_computed

    def __repr__(self):
        return f'{type(self).__name__}({self._elements!r})'

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._head is other._head
        return NotImplemented

    def __hash__(self):
        return hash(self._head)

    def __iter__(self):
        return iter(self._elements)

    @property
    def _head(self):
        if self._lazy_head is self._not_computed:
            self._lazy_head = sll.HashNode.from_iterable(self)
        return self._lazy_head


class TestHashNodeReentrantCachedEq(unittest.TestCase):
    """
    Tests for __new__ reentrancy bugs in sll.HashNode, with _CachedEq elements.

    These tests are equivalent to the _CachedEq doctests above, but as unittest
    tests. This is (1) so the unittest test runner, and the pytest test runner
    even without --doctest-modules, runs them, (2) to clarify the relationship
    between design decisions and which test case should be skipped, and (3) to
    facilitate comparison to the TestHashNodeReentrantDevious tests below.

    It is not a goal to thoroughly test the public interface of _CachedEq
    itself. These are really sll.HashNode tests, using _CachedEq.
    """

    def test_can_create_node_of_cached_eq_if_its_node_is_precomputed(self):
        """If reentrance is prevented, the node can always be created."""
        expected = ['r', 'e', 'e', 'n', 't', 'r', 'a', 'n', 't', '?']
        cached_eq = _CachedEq('reentrant?')
        hash(cached_eq)  # Precompute x.node, to avoid reentrance.
        node = sll.HashNode(cached_eq)  # Reentrance averted, so this works.
        actual = list(node.value)
        self.assertListEqual(actual, expected)

    @unittest.skip("We don't let sll.HashNode call itself through __hash__.")
    def test_can_create_node_of_cached_eq_if_its_node_is_not_precomputed(self):
        """
        Reentering sll.HashNode through __hash__ completes, returning the node.

        That is, it completes rather than deadlocking or raising an exception.
        """
        expected = ['s', 'a', 'b', 'o', 't', 'a', 'g', 'e']
        cached_eq = _CachedEq('sabotage')

        # This Reenters sll.HashNode.__new__ through _CachedEq.__hash__.
        node = sll.HashNode(cached_eq)

        actual = list(node.value)
        self.assertListEqual(actual, expected)

    def test_creating_node_of_cached_eq_without_precomputed_node_raises(self):
        """
        Reentering sll.HashNode through __hash__ raises a useful RuntimeError.

        That is, it raises RuntimeError and the message is as expected. This is
        in contrast to deadlocking or permitting the operation.
        """
        expected_message = (
            r'\AHashNode.__new__ reentered through __hash__ or __eq__\Z')

        cached_eq = _CachedEq('sabotage')

        with self.assertRaisesRegex(RuntimeError, expected_message):
            sll.HashNode(cached_eq)


class _DeviousBase:
    """
    "Correct" class to try to get sll.HashNode to make duplicates. For testing.

    See _CachedEq above for background. If one wishes to support types like
    _CachedEq whose __hash__ calls sll.HashNode, this facilitates checking that
    reentrance through __eq__ still raises RuntimeError, or that a *simple*
    attempt to exploit it to get two equivalent nodes is successfully stymied.

    The actual tests are in TestHashNodeReentrantDevious. Doctests are omitted,
    as they provide no convenient notation to ensure cleanup code always runs.
    (After the test, we break the heterogeneous cycle formed through "devious"
    objects, to depend less on TestHashNodeHeterogeneousCycles tests passing.)
    """

    __slots__ = ('_calls', 'node')

    def __init__(self):
        """Create an object that tries to make a duplicate sll.HashNode."""
        self._calls = 0
        self.node = None

    def __repr__(self):
        """Representation for debugging showing the obtained node, if any."""
        node_info = f'node at 0x{id(self.node):X}' if self.node else 'no node'
        return f'<{type(self).__name__}: _calls={self._calls}, {node_info}>'

    def __eq__(self, other):
        """
        Check if this devious object is the same as another devious object.

        A deliberately pathological __eq__ on an element type will always be
        able to fool sll.HashNode into making duplicates. The useful challenge
        is to do it in a way that reveals a bug in sll.HashNode. If x == y is
        sometimes True and sometimes False, on the same x and y, then at least
        one of x and y is, by definition, mutable. (Other notions of mutability
        exist, but that's the one that applies to the expectation in Python
        that calling hash on a mutable object raises TypeError.) Like most
        Python code that uses hashing, sll.HashNode assumes hashable objects it
        interacts with are immutable, encapsulation is respected, etc.

        What is significant about this __eq__ implementation is that it is
        consistent: when called multiple times with the same operands, it
        always returns the same result. It also does not violate encapsulation.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        # By now, with DeviousBase and DeviousDerived, self is DeviousBase.
        # Assume the second time we get here is table insertion. See tests.
        self._calls += 1
        if self.node is None and self._calls == 2:
            self.node = sll.HashNode(self)

        return self is other

    def __hash__(self):
        """Bad but consistent hashing. Guarantee a collision for simplicity."""
        return 42


class _DeviousDerived(_DeviousBase):
    """Trivial _DeviousBase subclass, to get predictable __eq__ asymmetry."""

    __slots__ = ()


class TestHashNodeReentrantDevious(unittest.TestCase):
    """
    Tests for __new__ reentrancy bugs in sll.HashNode, via element __eq__.

    This class has a single (non-skipped) test. It tries to use _DeviousBase
    and _DeviousDerived to fool sll.HashNode into making duplicate nodes by
    exploiting the need for sll.HashNode.__new__ to call _DeviousBase.__eq__
    indirectly (through the table implementation) while inserting a new node in
    the table. At that time, the node exists but isn't yet in the table. So if
    _DeviousBase.__eq__ can reenter sll.HashNode.__new__, it can get another
    node.

    The code under test should not take approaches specific to details of the
    test, because it would still have the bug the test is trying to find. In
    particular, adding pointless equality comparisons, so _DeviousBase.__eq__
    guesses wrong about which one is the table insertion, shouldn't be done.
    (_DeviousBase's real goal is clarity, not maximally robust deviousness.)
    """

    def setUp(self):
        """Create the two "devious" objects use for testing."""
        # First instance, to set things up. We must hold a reference to this.
        self._feint = _DeviousDerived()

        # Second instance, which will be self for the fateful __eq__ call.
        self._strike = _DeviousBase()

    def tearDown(self):
        """Break any heterogeneous cycles through the "devious" objects."""
        self._feint.node = self._strike.node = None

    @unittest.skip("We don't let sll.HashNode call itself through __eq__.")
    def test_effort_to_make_duplicate_nodes_is_defeated_without_error(self):
        """Duplicate nodes are somehow averted without stopping reentrance."""
        node1 = sll.HashNode(self._feint)

        if node1.value is not self._feint:
            raise Exception('unexpected failure to construct correct node #1')

        node2 = sll.HashNode(self._strike)

        if node2.value is not self._strike:
            raise Exception('unexpected failure to construct correct node #2')

        node3 = self._strike.node

        if node2.value != node3.value:
            raise Exception('unexpected failure to make equal elements')
        if node2.next_node is not node3.next_node:
            raise Exception('unexpected failure to make identical successors')

        self.assertIs(
            node2, node3,
            'Nodes of equal value and same next node should be the same node.')

    def test_effort_to_make_duplicate_nodes_is_defeated_by_runtime_error(self):
        """Duplicate nodes are averted by reentrance raising RuntimeError."""
        expected_message = (
            r'\AHashNode.__new__ reentered through __hash__ or __eq__\Z')

        _ = sll.HashNode(self._feint)

        with self.assertRaisesRegex(RuntimeError, expected_message):
            sll.HashNode(self._strike)


if __name__ == '__main__':
    unittest.main()
