#!/usr/bin/env python

"""Tests for sll.py."""

import gc
import itertools
import types
import unittest
import weakref

import graphviz
from parameterized import parameterized

import sll
import testing


class TestNode(unittest.TestCase):
    """Base class providing shared tests of sll.Node."""

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
        The second argument (next_node) must be an instance of the node type.

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

    def test_repr_shows_chain_recursively(self):
        expected = "Node('a', Node('b', Node('c', Node('d'))))"
        head = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        self.assertEqual(repr(head), expected)

    @parameterized.expand([
        ('one', 1),
        ('zero', 0),
        ('obj', object()),
        ('none', None),
    ])
    def test_is_truthy(self, _name, value):
        head = sll.Node(value)
        self.assertTrue(head)

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

    def test_from_iterable_returns_none_from_empty_sequence(self):
        head = sll.Node.from_iterable([])
        self.assertIsNone(head)

    def test_from_iterable_returns_none_from_empty_iterator(self):
        head = sll.Node.from_iterable(iter([]))
        self.assertIsNone(head)

    def test_from_iterable_finds_chain_from_nonempty_sequence(self):
        # NOTE: This test MUST be written to assign "expected" first.
        expected = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        actual = sll.Node.from_iterable('abcd')
        self.assertIs(actual, expected)

    def test_from_iterable_builds_chain_from_nonempty_sequence(self):
        # NOTE: This test MUST be written to assign "actual" first.
        actual = sll.Node.from_iterable('abcd')
        expected = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        self.assertIs(actual, expected)

    def test_from_iterable_builds_long_chain(self):
        head = sll.Node.from_iterable(range(9000))
        self.assertIsInstance(head, sll.Node)

    def test_from_iterable_long_chain_has_same_length_as_input(self):
        head = sll.Node.from_iterable(range(9000))

        length = 0
        node = head
        while node:
            length += 1
            node = node.next_node

        self.assertEqual(length, 9000)

    def test_from_iterable_long_chain_has_equal_values_to_input(self):
        head = sll.Node.from_iterable(range(9000))

        values = []
        node = head
        while node:
            values.append(node.value)
            node = node.next_node

        self.assertListEqual(values, list(range(9000)))

    def test_from_iterable_new_longer_chain_can_overlap_long_chain(self):
        shorter = sll.Node.from_iterable(range(9000))
        longer = sll.Node.from_iterable(range(-100, 9000))

        node = longer
        for _ in range(100):
            node = node.next_node

        self.assertIs(node, shorter)

    def test_from_iterable_new_shorter_chain_can_overlap_long_chain(self):
        longer = sll.Node.from_iterable(range(-100, 9000))
        shorter = sll.Node.from_iterable(range(9000))

        node = longer
        for _ in range(100):
            node = node.next_node

        self.assertIs(node, shorter)

    @parameterized.expand(['__eq__', '__ne__', '__hash__'])
    def test_type_uses_reference_equality_comparison(self, name):
        expected = getattr(object, name)
        actual = getattr(sll.Node, name)
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
        head1 = sll.Node('a', sll.Node('b', sll.Node('c', sll.Node('d'))))
        head2 = sll.Node('x', sll.Node('b', sll.Node('c', sll.Node('d'))))
        head3 = sll.Node(0)
        head4 = sll.Node.from_iterable(range(9000))

        with self.subTest('before any of head1-head5 are collectable'):
            testing.collect_if_not_ref_counting()
            self.assertEqual(sll.Node.count_instances(), 9006)

        head5 = sll.Node.from_iterable(range(-100, 9000))

        with self.subTest('after creating head5'):
            # We do not need to force a collection here regardless of platform,
            # since we have only created nodes since the last possibly forced
            # collection. (Of course, other code could concurrently be making
            # nodes or allowing them to be destroyed, but if so, this test is
            # already very unreliable, as detailed in the method docstring.)
            count = sll.Node.count_instances()
            self.assertEqual(count, 9106)

        del head4, head5

        with self.subTest('after deleting local variables head4 and head5'):
            testing.collect_if_not_ref_counting()
            count = sll.Node.count_instances()
            self.assertEqual(count, 6)

        head3 = head1

        with self.subTest('after rebinding the head3 local variable'):
            testing.collect_if_not_ref_counting()
            count = sll.Node.count_instances()
            self.assertEqual(count, 5)

        del head1

        with self.subTest('after deleting local variable head1'):
            testing.collect_if_not_ref_counting()  # To show no effect.
            count = sll.Node.count_instances()
            self.assertEqual(count, 5)

        del head3

        with self.subTest('after deleting local variable head3'):
            testing.collect_if_not_ref_counting()
            count = sll.Node.count_instances()
            self.assertEqual(count, 4)

        del head2

        with self.subTest('after deleting local variable head2'):
            testing.collect_if_not_ref_counting()
            count = sll.Node.count_instances()
            self.assertEqual(count, 0)

    @unittest.skip("The implementation does not break heterogeneous cycles.")
    def test_single_simple_heterogeneous_cycle_does_not_leak(self):
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
        # _head2 keep nodes alive and are deliberately never read (hence F841).
        _head1 = sll.Node('a', sll.Node('c'))  # noqa: F841
        _head2 = sll.Node('b', sll.Node('c'))  # noqa: F841

        graph = sll.Node.draw()
        self.assertIsInstance(graph, graphviz.Digraph)


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


class CachedEq:
    """
    Class to try to deadlock sll.Node if its lock isn't reentrant. For testing.

    CachedEq equality comparison and hashing use the global caching supplied by
    sll.Node to speed up subsequent comparisons. This just works:

    >>> x = CachedEq('reentrant?')
    >>> x
    CachedEq(['r', 'e', 'e', 'n', 't', 'r', 'a', 'n', 't', '?'])
    >>> hash(x) == hash(x)
    True
    >>> x == CachedEq('other')
    False
    >>> x == CachedEq('reentrant?')
    True

    Our CachedEq is instance is hashable, so it can be a value in an sll.Node:

    >>> sll.Node(x)
    Node(CachedEq(['r', 'e', 'e', 'n', 't', 'r', 'a', 'n', 't', '?']))

    But if a CachedEq instance whose SLL is not yet created is stored in an
    sll.Node, the sll.Node class's act of hashing the CachedEq instance causes
    another sll.Node object to be constructed while that "first" sll.Node
    object is being constructed. This deadlocks if the lock is non-reentrant:

    >>> sll.Node(CachedEq('sabotage'))  # doctest: +SKIP
    Node(CachedEq(['s', 'a', 'b', 'o', 't', 'a', 'g', 'e']))

    Making the lock reentrant is attractive. On a single thread, the code
    (being synchronous, and pairing acquisition and release) behaves as it
    would without locking. If we didn't need to worry about multiple threads,
    we would likely have written the same code, but without a lock. But would
    that have been right? Do reentrant sll.Node calls always behave correctly?

    Let's consider an approach that makes CachedEq work without a reentrant
    lock. sll.Node(x, n) looks up a key in a table. Calling __hash__ on that
    key causes x.__hash__ to be called. Now suppose _Key is the key type. If
    _Key were to precompute its __hash__ result in _Key.__init__, and if
    sll.Node.__new__ were to call _Key exactly once and before taking the lock,
    then sll.Node would work with CachedEq, even if the lock is non-reentrant.

    Implementing _Key reveals the problem with BOTH approaches. The result of
    __hash__ can be precomputed, because it really returns a prehash: a value
    depending only on the key, and not on hash table size. But looking up a key
    uses both __hash__ and __eq__. We can't usually precompute all possible
    results of __eq__. We could effectively achieve the goal of precomputing
    all possible results of __eq__ by ensuring the each value is represented by
    only one object at a time and doing identity comparison -- but that's hash
    consing, which is what we're trying to implement!

    It's feasible for sll.Node to support types like CachedEq, because after
    __hash__ is called successfully on a CachedEq instance, __eq__ on the same
    instance never calls sll.Node. Other types, intentionally or due to bugs,
    may call sll.Node from their __eq__ methods. This is tricky to make safe.
    After sll.Node.__new__(x, n) subscripts a table with a key whose __eq__
    method calls x.__eq__, doesn't find the key, and creates a new node, it
    subscripts the table again to insert the new node. This is a critical time:
    a node exists that isn't yet in the table. The operation of adding it to
    the table calls x.__eq__ before adding it, which could call sll.Node(x, n).

    Even though this problem is unrelated to threading, a non-reentrant lock
    prevented it. I don't know of a way to make reentering sll.Node through
    __eq__ safe in Python without considerably increasing code complexity.
    Instead, we can detect it and raise RuntimeError instead of deadlocking. We
    could support reentrance via __hash__ but not __eq__, thereby allowing
    types like CachedEq to work. But unless that is a specific design goal, I
    recommend against it, for simplicity. sll.Node doesn't need to work with
    CachedEq; the error just needs to be represented by a reasonable exception.

    >>> sll.Node(CachedEq('sabotage'))
    Traceback (most recent call last):
      ...
    RuntimeError: Node.__new__ reentered through __hash__ or __eq__
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
            self._lazy_head = sll.Node.from_iterable(self)
        return self._lazy_head


_NODE_CONSTRUCTION_IS_REENTRANT_THROUGH_HASH = False
"""Set this according to the design decision made. See CachedEq above."""


class TestCachedEq(unittest.TestCase):
    """
    Tests for sll.Node with CachedEq values.

    These tests are equivalent to the CachedEq doctests above, but as unittest
    tests. This is (1) so the unittest test runner, and by the pytest test
    runner even without --doctest-modules, runs them, (2) to clarify the
    relationship between design decisions and what test to skip, (3) to
    facilitate comparison to the TestDevious tests, below.

    It is not a goal to thoroughly test the public interface of CachedEq
    itself. These are really sll.Node tests, using CachedEq.
    """

    def test_can_create_node_of_cached_eq_if_its_node_is_precomputed(self):
        """If reentrance is prevented, the node can always be created."""
        expected = ['r', 'e', 'e', 'n', 't', 'r', 'a', 'n', 't', '?']
        cached_eq = CachedEq('reentrant?')
        hash(cached_eq)  # Precompute x.node, to avoid reentrance.
        node = sll.Node(cached_eq)  # Reentrance averted, so this works.
        actual = list(node.value)
        self.assertListEqual(actual, expected)

    @unittest.skipUnless(_NODE_CONSTRUCTION_IS_REENTRANT_THROUGH_HASH,
        'Only run if sll.Node permits calling itself through __hash__.')
    def test_can_create_node_of_cached_eq_if_its_node_is_not_precomputed(self):
        """
        Reentering sll.Node through __hash__ is permitted, returning the node.

        That is, it completes rather than deadlocking or raising an exception.
        """
        expected = ['s', 'a', 'b', 'o', 't', 'a', 'g', 'e']
        cached_eq = CachedEq('sabotage')
        node = sll.Node(cached_eq)  # Reenters Node through CachedEq.__hash__.
        actual = list(node.value)
        self.assertListEqual(actual, expected)

    @unittest.skipIf(_NODE_CONSTRUCTION_IS_REENTRANT_THROUGH_HASH,
        'Only run if sll.Node prohibits calling itself through __hash__.')
    def test_creating_node_of_cached_eq_without_precomputed_node_raises(self):
        """
        Reentering sll.Node through __hash__ raises a useful RuntimeError.

        That is, it raises RuntimeError and the message is as expected. This is
        in contrast to deadlocking or permitting the operation.
        """
        expected_message = (
            r'\ANode.__new__ reentered through __hash__ or __eq__\Z')
        cached_eq = CachedEq('sabotage')
        with self.assertRaisesRegex(RuntimeError, expected_message):
            sll.Node(cached_eq)


class DeviousBase:
    """
    "Correct" class that tries to get sll.Node to make duplicates. For testing.

    See CachedEq above for background. In case you want to support types like
    CachedEq whose __hash__ calls sll.Node, this facilitates checking that
    reentrance through __eq__ still raises RuntimeError, or that a simple
    attempt to exploit it to get two equivalent nodes is successfully stymied.

    The actual tests are in TestDevious below. They are not replicated in
    doctests, because there is no reliable way to break the cycle between
    the DeviousDerived object's node attribute and the node that holds a
    reference to the

    >>> class DeviousDerived(DeviousBase): __slots__ = ()
    >>> node1 = sll.Node(DeviousDerived())  # Hold this strong reference.
    >>> node2 = sll.Node(DeviousBase())
    >>> node3 = node2.value.node
    >>> node2.value == node3.value and node2.next_node is node3.next_node
    True
    >>> node2 is node3  # Test that sll.Node somehow stymies this deviousness.
    True
    """

    __slots__ = ('_calls', 'node')

    def __init__(self):
        """Create a devious object that tries to make a duplicate sll.Node."""
        self._calls = 0
        self.node = None

    def __repr__(self):
        """Representation for debugging showing the obtained node, if any."""
        node_info = f'node at 0x{id(self.node):X}' if self.node else 'no node'
        return f'<{type(self).__name__}: _calls={self._calls}, {node_info}>'

    def __eq__(self, other):
        """
        Check if this is devious object is the same as another devious object.

        It is trivial to implement __eq__ in a way that fools sll.Node into
        making duplicate nodes. The challenge is to do it in a way that reveals
        a bug in sll.Node. If x == y is sometimes True and sometimes False, on
        the same objects x and y, then at least one of x and y is mutable (by
        definition). Like most Python code that uses hashing, the code of
        sll.Node relies on hashable objects it interacts with being immutable.
        See also ImportantPoint below for more ways to "fool" sll.Node in ways
        that sll.Node should not, and cannot reasonably, handle.

        What is significant about this __eq__ implementation is that it is
        consistent: when called multiple times with the same operands, it
        always returns the same result. It also does not violate encapsulation.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        # By now, with DeviousBase and DeviousDerived, self is DeviousBase.
        # Assume the second time we get here is table insertion. See doctests.
        self._calls += 1
        if self.node is None and self._calls == 2:
            self.node = sll.Node(self)

        return self is other

    def __hash__(self):
        """Bad but consistent hashing. Guarantee a collision for simplicity."""
        return 42


class ImportantPoint:
    """
    Demonstration that sll.Node can be "fooled" in ways that are not its fault.

    Here, we use objects we reasonably consider immutable, except we break the
    rules and mutate them by assigning to non-public attributes that make up
    part of the objects' values. Here, the bug is in the code that uses the
    ImportantPoint class incorrectly. Neither ImportantPoint nor sll.Node
    should, or reasonably could, be changed to work with or even catch this.

    We will be corrupting shared state, at least temporarily. To limit the bad
    effect, we ensure the chains we form won't be reused, due to all containing
    an inaccessible object not equal to values in any future unrelated SLLs:

    >>> last = sll.Node(object())

    >>> node1 = sll.Node(ImportantPoint(30, 40, 50), last)
    >>> node2 = sll.Node(ImportantPoint(30, 41, 50), last)
    >>> node2.value._y -= 1  # The bug is here and nowhere else.

    >>> node1 is node2, node1 == node2
    (False, False)
    >>> node1.value == node2.value and node1.next_node is node2.next_node
    True

    >>> head1 = sll.Node('a', sll.Node('b', sll.Node('c', node1)))
    >>> head2 = sll.Node('a', sll.Node('b', sll.Node('c', node2)))
    >>> head1 is head2, head1 == head2
    (False, False)
    >>> list(sll.traverse(head1)) == list(sll.traverse(head2))
    True

    Other variations on that bug include writing to the private backing
    attribute used to provide the value attribute on an sll.Node instance,
    accessing and modifying the private table sll.Node uses to track its
    instances, or assigning a different function to sll.Node.__new__.
    """

    __slots__ = ('_x', '_y', '_z')

    def __init__(self, x, y, z):
        """Make an important point."""
        self._x = x
        self._y = y
        self._z = z

    def __repr__(self):
        """Python code representation."""
        return f'{type(self).__name__}({self.x!r}, {self.y!r}, {self.z!r})'

    def __eq__(self, other):
        """Check for equal corresponding coordinates."""
        if isinstance(other, type(self)):
            return (self.x, self.y, self.z) == (other.x, other.y, other.z)
        return NotImplemented

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    @property
    def x(self):
        """The x-coordinate."""
        return self._x

    @property
    def y(self):
        """The y-coordinate."""
        return self._y

    @property
    def z(self):
        """The z-coordinate."""
        return self._z


if __name__ == '__main__':
    unittest.main()
