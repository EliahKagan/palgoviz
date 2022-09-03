#!/usr/bin/env python

"""Tests for mappings.py."""

from abc import ABC, abstractmethod
from collections.abc import ItemsView, KeysView, MutableMapping, ValuesView
from fractions import Fraction
import unittest

from parameterized import parameterized

from mappings import (
    UnsortedFlatTable,
    SortedFlatTable,
    BinarySearchTree,
    DirectAddressTable,
    HashTable,
)


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

    def test_no_instance_dictionary(self):
        """
        No work should be done with dict, not even as __dict__.

        See the mappings module docstring for details.
        """
        table = self.instantiate()
        with self.assertRaises(AttributeError):
            table.__dict__


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

    _parameterize_by_capacity = parameterized.expand([
        (f'cap{cap}', cap)
        for cap in [*range(11), 100, 256, 1000, 1017, 5000, 50_041]
    ])

    @property
    def mapping_type(self):
        return DirectAddressTable

    def instantiate(self, *args, **kwargs):
        return DirectAddressTable(256, *args, **kwargs)

    def test_cannot_construct_without_capacity_arg(self):
        with self.assertRaises(TypeError):
            DirectAddressTable()

    @parameterized.expand([
        ('neg1', -1, '-1'),
        ('neg2', -2, '-2'),
        ('neg100', -100, '-100'),
    ])
    def test_capacity_must_be_nonnegative(self, _name,
                                          capacity, capacity_text):
        expected_message = (r'\Acapacity cannot be negative, got %s\Z'
                            % capacity_text)

        with self.assertRaisesRegex(ValueError, expected_message):
            DirectAddressTable(capacity)

    @parameterized.expand([
        ('float', 256.0,),
        ('Fraction', Fraction(256)),
        ('str', '256'),
    ])
    def test_capacity_must_be_int(self, type_text, capacity):
        expected_message = (r"\Acapacity must be 'int', not '%s'\Z"
                            % type_text)

        with self.assertRaisesRegex(TypeError, expected_message):
            DirectAddressTable(capacity)

    def test_negative_non_int_capacity_is_a_type_error(self):
        """Whenever TypeError applies, it is raised, not ValueError."""
        expected_message = r"\Acapacity must be 'int', not 'float'\Z"

        with self.assertRaisesRegex(TypeError, expected_message):
            DirectAddressTable(-1.0)

    @_parameterize_by_capacity
    def test_capacity_has_capacity(self, _name, capacity):
        table = DirectAddressTable(capacity)
        self.assertEqual(table.capacity, capacity)

    @_parameterize_by_capacity
    def test_capacity_can_be_given_as_keyword_arg(self, _name, capacity):
        table = DirectAddressTable(capacity=capacity)
        self.assertEqual(table.capacity, capacity)


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
