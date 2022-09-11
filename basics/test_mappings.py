#!/usr/bin/env python

"""Tests for mappings.py."""

from abc import ABC, abstractmethod
from collections.abc import ItemsView, KeysView, MutableMapping, ValuesView
from fractions import Fraction
import random
from types import MappingProxyType
import unittest

from parameterized import parameterized

from mappings import (
    UnsortedFlatTable,
    SortedFlatTable,
    BinarySearchTree,
    DirectAddressTable,
    HashTable,
)


def _make_example_items(keys, *, seed):
    """Create an example with the given keys in scrambled order."""
    keys = list(keys)
    random.Random(seed).shuffle(keys)
    return MappingProxyType({key: object() for key in keys})


_parameterize_by_empty_iterable = parameterized.expand([
    ('tuple', ()),
    ('list', []),
    ('iterator', iter([])),  # Non-generator iterator.
    ('generator', (x for x in ())),
])
"""Parameterize a test method by empty iterables (some of them iterators)."""


_parameterize_by_empty_mapping = parameterized.expand([
    ('dict', {}),
    ('mappingproxy', MappingProxyType({})),
])
"""Parameterize a test method by empty mappings."""


_parameterize_by_items = parameterized.expand([
    ('len1', 1, MappingProxyType({42: 'A'})),
    ('len2', 2, MappingProxyType({42: 'A', 3: 'C'})),
    ('len3', 3, MappingProxyType({42: 'A', 3: 'C', 255: 'B'})),
    ('len4', 4, MappingProxyType({42: 'A', 3: 'C', 255: 'B', 76: 'D'})),
    ('len256', 256, _make_example_items(range(256), seed=3731775464805526349)),
])
"""Parameterize a test method by different-sized mappings giving items."""


class _TestMutableMapping(ABC):
    """
    Tests shared by all mutable mappings in mappings.py.

    Concrete derived classes, in addition to overriding mapping_type and, if
    the default implementation is unsuitable, overriding instantiate, are
    expected to inherit (directly or indirectly) from unittest.TestCase.
    """

    @property
    @abstractmethod
    def mapping_type(self):
        """The implementation being tested."""
        raise NotImplementedError

    def instantiate(self, *args, **kwargs):
        """
        Construct an instance of the implementation (the class under test).

        This may be called with no arguments to create an empty instance, or
        with positional and/or keyword arguments to pass to the implementation.
        It is expected to return an empty instance that accepts 0, 1, ..., 255
        as keys. It may, and in most cases will, also accept many other keys.
        This should only be overridden if forwarding *args and **kwargs to the
        mapping type does not achieve this. This method exists so mappings that
        are constructed in unusual ways, particularly DirectAddressTable, can
        share tests with mappings constructed in more ordinary ways.
        """
        return self.mapping_type(*args, **kwargs)

    def test_class_is_a_mutable_mapping_type(self):
        self.assertTrue(issubclass(self.mapping_type, MutableMapping))

    def test_instance_is_a_mutable_mapping(self):
        table = self.instantiate()
        self.assertIsInstance(table, MutableMapping)

    def test_items_gives_items_view_instance(self):
        """The items method gives a direct or indirect ItemsView instance."""
        table = self.instantiate()
        items = table.items()
        self.assertIsInstance(items, ItemsView)

    def test_keys_gives_keys_view_instance(self):
        """The keys method gives a direct or indirect KeysView instance."""
        table = self.instantiate()
        keys = table.keys()
        self.assertIsInstance(keys, KeysView)

    def test_values_gives_values_view_instance(self):
        """The values method gives a direct or indirect ValuesView instance."""
        table = self.instantiate()
        values = table.values()
        self.assertIsInstance(values, ValuesView)

    def test_not_hashable(self):
        """A mutable type should not be hashable."""
        table = self.instantiate()
        with self.assertRaises(TypeError):
            hash(table)

    def test_cannot_create_new_attributes(self):
        table = self.instantiate()
        with self.assertRaises(AttributeError):
            table.hopefully_nonexistent_attribute = 42

    def test_no_instance_dictionary(self):
        """
        No work should be done with dict, not even as __dict__.

        See the mappings module docstring for details.
        """
        table = self.instantiate()
        with self.assertRaises(AttributeError):
            table.__dict__

    def test_simplest_construction_gives_falsy_instance(self):
        table = self.instantiate()
        self.assertFalse(table)

    def test_simplest_construction_gives_zero_size_instance(self):
        table = self.instantiate()
        self.assertEqual(len(table), 0)

    @_parameterize_by_empty_iterable
    def test_construction_from_empty_iterable_gives_falsy_instance(self, _name,
                                                                   iterable):
        table = self.instantiate(iterable)
        self.assertFalse(table)

    @_parameterize_by_empty_iterable
    def test_construction_from_empty_iterable_gives_zero_size_instance(
            self, _name, iterable):
        table = self.instantiate(iterable)
        self.assertEqual(len(table), 0)

    @_parameterize_by_empty_mapping
    def test_construction_from_empty_mapping_gives_falsy_instance(self, _name,
                                                                  mapping):
        table = self.instantiate(mapping)
        self.assertFalse(table)

    @_parameterize_by_empty_mapping
    def test_construction_from_empty_mapping_gives_zero_size_instance(self,
                                                                      _name,
                                                                      mapping):
        table = self.instantiate(mapping)
        self.assertEqual(len(table), 0)

    def test_empty_has_falsy_items_view(self):
        table = self.instantiate()
        items = table.items()
        self.assertFalse(items)

    def test_empty_has_zero_size_items_view(self):
        table = self.instantiate()
        items = table.items()
        self.assertEqual(len(items), 0)

    def test_empty_has_falsy_keys_view(self):
        table = self.instantiate()
        keys = table.keys()
        self.assertFalse(keys)

    def test_empty_has_zero_size_keys_view(self):
        table = self.instantiate()
        keys = table.keys()
        self.assertEqual(len(keys), 0)

    def test_empty_has_falsy_values_view(self):
        table = self.instantiate()
        values = table.values()
        self.assertFalse(values)

    def test_empty_has_zero_size_values_view(self):
        table = self.instantiate()
        values = table.values()
        self.assertEqual(len(values), 0)

    @_parameterize_by_items
    def test_construction_from_nonempty_sequence_gives_truthy_instance(
            self, _name, _length, mapping):
        items = list(mapping.items())
        table = self.instantiate(items)
        self.assertTrue(table)

    @_parameterize_by_items
    def test_construction_from_nonempty_items_view_gives_truthy_instance(
            self, _name, _length, mapping):
        items = mapping.items()
        table = self.instantiate(items)
        self.assertTrue(table)

    @_parameterize_by_items
    def test_construction_from_nonempty_mapping_gives_truthy_instance(
            self, _name, _length, mapping):
        table = self.instantiate(mapping)
        self.assertTrue(table)

    @_parameterize_by_items
    def test_construction_from_nonempty_sequence_has_same_len(self, _name,
                                                              length, mapping):
        items = list(mapping.items())
        table = self.instantiate(items)
        self.assertEqual(len(table), length)

    @_parameterize_by_items
    def test_construction_from_nonempty_items_view_has_same_len(self, _name,
                                                                length,
                                                                mapping):
        items = mapping.items()
        table = self.instantiate(items)
        self.assertEqual(len(table), length)

    @_parameterize_by_items
    def test_construction_from_nonempty_mapping_has_same_len(self, _name,
                                                             length, mapping):
        table = self.instantiate(mapping)
        self.assertEqual(len(table), length)

    # @_parameterize_by_items
    # def test_construction_from_nonempty_sequence_has_same_items(self, _name,
    #                                                             _length,
    #                                                             mapping):

    # FIXME: Write the (many) rest of these tests.


class TestUnsortedFlatTable(_TestMutableMapping, unittest.TestCase):
    """Tests for UnsortedFlatTable."""

    @property
    def mapping_type(self):
        return UnsortedFlatTable


class TestSortedFlatTable(_TestMutableMapping, unittest.TestCase):
    """Tests for SortedFlatTable."""

    @property
    def mapping_type(self):
        return SortedFlatTable


class TestBinarySearchTree(_TestMutableMapping, unittest.TestCase):
    """Tests for BinarySearchTree."""

    @property
    def mapping_type(self):
        return BinarySearchTree


class TestDirectAddressTable(_TestMutableMapping, unittest.TestCase):
    """Tests for DirectAddressTable."""

    def _parameterize_by_capacity(*, minimum):
        """Parameterize a test method by a capacity or capacity delta."""
        capacities = [*range(minimum, 7), 100, 256, 1000, 1017, 5000, 50_041]
        rows = [(f'cap{cap}', cap) for cap in capacities]
        return parameterized.expand(rows)

    _parameterize_by_negative = parameterized.expand([
        ('neg1', -1, '-1'),
        ('neg2', -2, '-2'),
        ('neg100', -100, '-100'),
    ])
    """Parameterize a test method by a negative int."""

    _parameterize_by_non_int = parameterized.expand([
        ('float', 128.0,),
        ('Fraction', Fraction(128)),
        ('str', '128'),
    ])
    """Parameterize a test method by a non-int type-name and value."""

    @property
    def mapping_type(self):
        return DirectAddressTable

    def instantiate(self, *args, **kwargs):
        return DirectAddressTable(256, *args, **kwargs)

    def test_cannot_construct_without_capacity_arg(self):
        with self.assertRaises(TypeError):
            DirectAddressTable()

    @_parameterize_by_negative
    def test_capacity_must_be_nonnegative(self, _name,
                                          capacity, capacity_text):
        expected_message = (r'\Acapacity cannot be negative, got %s\Z'
                            % capacity_text)

        with self.assertRaisesRegex(ValueError, expected_message):
            DirectAddressTable(capacity)

    @_parameterize_by_non_int
    def test_capacity_must_be_int(self, type_text, capacity):
        expected_message = (r"\Acapacity must be 'int', not '%s'\Z"
                            % type_text)

        with self.assertRaisesRegex(TypeError, expected_message):
            DirectAddressTable(capacity)

    def test_negative_non_int_capacity_is_type_error(self):
        """Whenever TypeError applies, it is raised, not ValueError."""
        expected_message = r"\Acapacity must be 'int', not 'float'\Z"

        with self.assertRaisesRegex(TypeError, expected_message):
            DirectAddressTable(-1.0)

    @_parameterize_by_capacity(minimum=0)
    def test_capacity_has_capacity(self, _name, capacity):
        table = DirectAddressTable(capacity)
        self.assertEqual(table.capacity, capacity)

    @_parameterize_by_capacity(minimum=0)
    def test_capacity_can_be_given_as_keyword_arg(self, _name, capacity):
        table = DirectAddressTable(capacity=capacity)
        self.assertEqual(table.capacity, capacity)

    def test_cannot_change_capacity(self):
        expected_message = r"\Acan't set attribute 'capacity'\Z"

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(AttributeError, expected_message):
            table.capacity = 512

    @_parameterize_by_capacity(minimum=0)
    def test_getting_too_high_key_is_index_error(self, _name, delta):
        capacity = 256
        key = capacity + delta
        table = DirectAddressTable(capacity)
        with self.assertRaises(IndexError):
            table[key]

    @_parameterize_by_capacity(minimum=0)
    def test_setting_too_high_key_is_index_error(self, _name, delta):
        capacity = 256
        key = capacity + delta
        table = DirectAddressTable(capacity)
        with self.assertRaises(IndexError):
            table[key] = 'foo'

    @_parameterize_by_capacity(minimum=0)
    def test_deleting_too_high_key_is_index_error(self, _name, delta):
        capacity = 256
        key = capacity + delta
        table = DirectAddressTable(capacity)
        with self.assertRaises(IndexError):
            del table[key]

    @_parameterize_by_negative
    def test_getting_negative_key_is_index_error(self, _name, key, _):
        table = DirectAddressTable(256)
        with self.assertRaises(IndexError):
            table[key]

    @_parameterize_by_negative
    def test_setting_negative_key_is_index_error(self, _name, key, _):
        table = DirectAddressTable(256)
        with self.assertRaises(IndexError):
            table[key] = 'foo'

    @_parameterize_by_negative
    def test_deleting_negative_key_is_index_error(self, _name, key, _):
        table = DirectAddressTable(256)
        with self.assertRaises(IndexError):
            del table[key]

    @_parameterize_by_non_int
    def test_getting_non_int_key_is_type_error(self, type_text, key):
        expected_message = (r"\Akey must be 'int', not '%s'\Z" % type_text)

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(TypeError, expected_message):
            table[key]

    @_parameterize_by_non_int
    def test_setting_non_int_key_is_type_error(self, type_text, key):
        expected_message = (r"\Akey must be 'int', not '%s'\Z" % type_text)

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(TypeError, expected_message):
            table[key] = 'foo'

    @_parameterize_by_non_int
    def test_deleting_non_int_key_is_type_error(self, type_text, key):
        expected_message = (r"\Akey must be 'int', not '%s'\Z" % type_text)

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(TypeError, expected_message):
            del table[key]

    def test_getting_negative_non_int_key_is_type_error(self):
        expected_message = r"\Akey must be 'int', not 'float'\Z"

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(TypeError, expected_message):
            table[-1.0]

    def test_setting_negative_non_int_key_is_type_error(self):
        expected_message = r"\Akey must be 'int', not 'float'\Z"

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(TypeError, expected_message):
            table[-1.0] = 'foo'

    def test_deleting_negative_non_int_key_is_type_error(self):
        expected_message = r"\Akey must be 'int', not 'float'\Z"

        table = DirectAddressTable(256)
        with self.assertRaisesRegex(TypeError, expected_message):
            del table[-1.0]

    @_parameterize_by_capacity(minimum=1)
    def test_getting_unset_zero_key_is_key_error(self, _name, capacity):
        """Getting an absent but in-range key is KeyError, not IndexError."""
        table = DirectAddressTable(capacity)
        with self.assertRaises(KeyError):
            table[0]

    @_parameterize_by_capacity(minimum=1)
    def test_deleting_unset_zero_key_is_key_error(self, _name, capacity):
        """Deleting an absent but in-range key is KeyError, not IndexError."""
        table = DirectAddressTable(capacity)
        with self.assertRaises(KeyError):
            del table[0]

    @_parameterize_by_capacity(minimum=1)
    def test_can_set_then_get_zero_key(self, _name, capacity):
        table = DirectAddressTable(capacity)
        table[0] = 'foo'
        self.assertEqual(table[0], 'foo')

    @_parameterize_by_capacity(minimum=1)
    def test_can_set_then_reset_then_get_zero_key(self, _name, capacity):
        table = DirectAddressTable(capacity)
        table[0] = 'foo'
        table[0] = 'bar'
        self.assertEqual(table[0], 'bar')

    @_parameterize_by_capacity(minimum=1)
    def test_can_set_then_delete_zero_key(self, _name, capacity):
        """Setting and deleting at 0 works, then getting raises KeyError."""
        table = DirectAddressTable(capacity)
        table[0] = 'foo'
        del table[0]
        with self.assertRaises(KeyError):
            table[0]

    @_parameterize_by_capacity(minimum=2)
    def test_getting_unset_max_key_is_key_error(self, _name, capacity):
        """Getting an absent but in-range key is KeyError, not IndexError."""
        table = DirectAddressTable(capacity)
        with self.assertRaises(KeyError):
            table[capacity - 1]

    @_parameterize_by_capacity(minimum=2)
    def test_deleting_unset_max_key_is_key_error(self, _name, capacity):
        """Deleting an absent but in-range key is KeyError, not IndexError."""
        table = DirectAddressTable(capacity)
        with self.assertRaises(KeyError):
            del table[capacity - 1]

    @_parameterize_by_capacity(minimum=2)
    def test_can_set_then_get_max_key(self, _name, capacity):
        table = DirectAddressTable(capacity)
        table[capacity - 1] = 'foo'
        self.assertEqual(table[capacity - 1], 'foo')

    @_parameterize_by_capacity(minimum=2)
    def test_can_set_then_reset_then_get_max_key(self, _name, capacity):
        table = DirectAddressTable(capacity)
        table[capacity - 1] = 'foo'
        table[capacity - 1] = 'bar'
        self.assertEqual(table[capacity - 1], 'bar')

    @_parameterize_by_capacity(minimum=2)
    def test_can_set_then_delete_max_key(self, _name, capacity):
        """
        Setting then deleting capacity - 1 works, then getting raises KeyError.
        """
        table = DirectAddressTable(capacity)
        table[capacity - 1] = 'foo'
        del table[capacity - 1]
        with self.assertRaises(KeyError):
            table[capacity - 1]


class TestHashTable(_TestMutableMapping, unittest.TestCase):
    """Tests for HashTable."""

    @property
    def mapping_type(self):
        return HashTable


# FIXME: Salvage stuff suitable to test DirectAddressTable. Delete this class.
import pytest  # Temporary import so the module can be loaded (going away).
class OldTestIntKeyTable:
    """Tests for the IntKeyTable class, a direct address table."""

    __slots__ = ()

    def test_type_is_a_mutable_mapping_type(self):
        assert issubclass(IntKeyTable, MutableMapping)

    def test_construction_actually_gives_a_mutable_mapping(self):
        table = IntKeyTable(0, 5)
        assert isinstance(table, MutableMapping)

    @pytest.mark.parametrize('n', [0, 1, 3, 4])
    def test_must_construct_with_two_arguments(self, n):
        with pytest.raises(TypeError):
            IntKeyTable(*range(n))

    @pytest.mark.parametrize('start, stop', [(0.0, 1.0), (0, 1.0), (0.0, 1)])
    def test_must_construct_with_ints(self, start, stop):
        with pytest.raises(TypeError):
            IntKeyTable(start, stop)

    @pytest.mark.parametrize('stop, start', [(1.0, 0.0), (1.0, 0), (1, 0.0)])
    def test_wrong_value_non_ints_fail_as_non_ints(self, start, stop):
        with pytest.raises(TypeError):
            IntKeyTable(start, stop)

    @pytest.mark.parametrize('start, stop', [(3, 1), (1, 0), (-1, -2)])
    def test_stop_must_not_precede_start(self, start, stop):
        with pytest.raises(ValueError):
            IntKeyTable(start, stop)

    @pytest.mark.parametrize('start, stop', [(1, 3), (-1, 4), (3, 10)])
    def test_start_has_start_value(self, start, stop):
        table = IntKeyTable(start, stop)
        assert table.start == start

    @pytest.mark.parametrize('start, stop, attempted_new_start', [
        (1, 3, -1),
        (-1, 4, 0),
        (3, 10, 5),
    ])
    def test_start_is_read_only(self, start, stop, attempted_new_start):
        table = IntKeyTable(start, stop)
        with pytest.raises(AttributeError):
            table.start = attempted_new_start

    @pytest.mark.parametrize('start, stop', [(1, 3), (-1, 4), (3, 10)])
    def test_stop_has_stop_value(self, start, stop):
        table = IntKeyTable(start, stop)
        assert table.stop == stop

    @pytest.mark.parametrize('start, stop, attempted_new_stop', [
        (1, 3, 2),
        (-1, 4, 5),
        (3, 10, 8),
    ])
    def test_stop_is_read_only(self, start, stop, attempted_new_stop):
        table = IntKeyTable(start, stop)
        with pytest.raises(AttributeError):
            table.stop = attempted_new_stop

    @pytest.mark.parametrize('start, stop, capacity', [
        (1, 3, 2),
        (-1, 4, 5),
        (3, 10, 7),
    ])
    def test_capacity_is_start_stop_distance(self, start, stop, capacity):
        table = IntKeyTable(start, stop)
        assert table.capacity == capacity

    @pytest.mark.parametrize('start, stop, attempted_new_capacity', [
        (1, 3, 3),
        (-1, 4, 2),
        (3, 10, 9),
    ])
    def test_capacity_is_read_only(self, start, stop, attempted_new_capacity):
        table = IntKeyTable(start, stop)
        with pytest.raises(AttributeError):
            table.capacity = attempted_new_capacity

    @pytest.mark.parametrize('start, stop', [(1, 3), (-1, 4), (1, 8)])
    def test_initially_falsy(self, start, stop):
        table = IntKeyTable(start, stop)
        assert not table

    @pytest.mark.parametrize('start, stop', [(1, 3), (-1, 4), (1, 8)])
    def test_initial_len_is_zero(self, start, stop):
        table = IntKeyTable(start, stop)
        assert len(table) == 0

    @pytest.mark.parametrize('start, stop', [(1, 3), (-1, 4), (1, 8)])
    def test_initial_iter_is_empty(self, start, stop):
        table = IntKeyTable(start, stop)
        it = iter(table)
        with pytest.raises(StopIteration):
            next(it)

    @pytest.mark.parametrize('start, stop', [(1, 3), (-1, 4), (1, 8)])
    def test_iter_after_initial_set_yields_single_key(self, start, stop):
        table = IntKeyTable(start, stop)
        table[2] = 'the second loneliest number'
        assert list(table) == [2]

    @pytest.mark.parametrize('start, stop', [(0, 3), (-1, 4), (1, 8)])
    def test_iter_after_two_sets_yields_sorted_keys(self, start, stop):
        table = IntKeyTable(start, stop)
        table[2] = 'the second loneliest number'
        table[1] = 'even lonelier'
        assert list(table) == [1, 2]

    def test_keys_returns_a_keys_view(self, prebuilt_ikt):
        assert isinstance(prebuilt_ikt.keys(), KeysView)

    def test_values_returns_a_values_view(self, prebuilt_ikt):
        assert isinstance(prebuilt_ikt.values(), ValuesView)

    def test_items_returns_an_items_view(self, prebuilt_ikt):
        assert isinstance(prebuilt_ikt.items(), ItemsView)

    def test_cannot_create_new_attributes(self):
        table = IntKeyTable(0, 5)
        with pytest.raises(AttributeError):
            table.color = 'green'

    def test_not_hashable(self):
        """IntKeyTable is a mutable type, so it shouldn't be hashable."""
        table = IntKeyTable(0, 5)
        with pytest.raises(TypeError):
            hash(table)


if __name__ == '__main__':
    unittest.main()
