#!/usr/bin/env python

"""Tests for mappings.py."""

from abc import ABC, abstractmethod
from collections.abc import ItemsView, KeysView, MutableMapping, ValuesView
import unittest

from mappings import (
    UnsortedFlatTable,
    SortedFlatTable,
    BinarySearchTree,
    DirectAddressTable,
    HashTable,
)


class _TestMutableMapping(ABC):
    """Tests shared by all mutable mappings in mappings.py."""

    @property
    @abstractmethod
    def mapping_type(self):
        """The implementation being tested."""
        raise NotImplementedError

    def instantiate(self):
        """Construct an instance of the implementation."""
        return self.mapping_type()

    def test_type_is_a_mutable_mapping_type(self):
        self.assertTrue(issubclass(self.mapping_type, MutableMapping))

    def test_construction_actually_gives_a_mutable_mapping(self):
        table = self.instantiate()
        self.assertIsInstance(table, MutableMapping)

    def test_items_gives_items_view(self):
        table = self.instantiate()
        items = table.items()
        self.assertIsInstance(items, ItemsView)

    def test_keys_gives_keys_view(self):
        table = self.instantiate()
        keys = table.keys()
        self.assertIsInstance(keys, KeysView)

    def test_values_gives_values_view(self):
        table = self.instantiate()
        values = table.values()
        self.assertIsInstance(values, ValuesView)


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

    @property
    def mapping_type(self):
        return DirectAddressTable

    def instantiate(self):
        return DirectAddressTable(capacity=256)


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
