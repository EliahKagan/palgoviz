#!/usr/bin/env python

"""
pytest tests for the simple code in simple.py.

The purpose of this module is to introduce and practice techniques for writing
tests with the pytest module (augmented with the pytest-subtest package).

See also test_simple.py for similar tests using unittest, not pytest.
"""

from fractions import Fraction
import sys

import pytest  # NOTE: Often we do NOT need this import to write pytest tests.


from simple import (
    MY_NONE,
    MulSquarer,
    PowSquarer,
    Squarer,
    Toggle,
    Widget,
    alert,
    answer,
    bail_if,
    is_sorted,
    make_squarer,
    make_toggle,
    make_toggle_alt,
)


def test_my_none_is_none():
    assert MY_NONE is None


@pytest.fixture
def widget():
    """Supply a newly created Widget instance for testing."""
    return Widget('vast', 'mauve')  # Arrange


def test_widget_size_attribute_has_size(widget):
    assert widget.size == 'vast'


def test_widget_color_attribute_has_color(widget):
    assert widget.color == 'mauve'


def test_widget_size_can_be_changed(widget):
    widget.size = 'just barely visible'
    assert widget.size == 'just barely visible'


def test_widget_color_can_be_changed(widget):
    widget.color = 'royal purple'  # Ac.
    assert widget.color == 'royal purple'


def test_widget_disallows_new_attribute_creation(widget):
    with pytest.raises(AttributeError):
        widget.favorite_desert = 'Sahara'


def test_the_answer_is_42():
    assert answer() == 42


def test_the_answer_is_an_int():
    assert isinstance(answer(), int)


def test_empty_list_is_sorted():
    items = []
    assert is_sorted(items)


def test_empty_generator_is_sorted():
    items = (x for x in ())
    assert is_sorted(items)


def test_one_element_list_is_sorted():
    items = [76]
    assert is_sorted(items)


def test_ascending_two_element_list_is_sorted():
    items = ['a', 'b']
    assert is_sorted(items)


@pytest.mark.parametrize('_kind, items', [
    ('strings', ['b', 'a']),
    ('integers', [3, 2]),
])
def test_descending_two_element_list_is_not_sorted(_kind, items):
    assert not is_sorted(items)


@pytest.mark.parametrize('_kind, items', [
    ('strings', (x for x in ('b', 'a'))),
    ('integers', (x for x in (3, 2))),
])
def test_descending_two_element_generator_is_not_sorted(_kind, items):
    assert not is_sorted(items)


def test_ascending_two_element_generator_is_sorted():
    items = (ch for ch in 'ab')
    assert is_sorted(items)


def test_equal_two_element_list_is_sorted():
    items = ['a', 'a']
    assert is_sorted(items)


def test_equal_two_element_generator_is_sorted():
    items = (ch for ch in 'aa')
    assert is_sorted(items)


def test_sorted_short_by_nontrivial_list_is_sorted():
    items = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
    assert is_sorted(items)


def test_unsorted_short_but_nontrivial_list_is_unsorted():
    items = ['bar', 'eggs', 'foo', 'ham', 'foobar', 'quux', 'baz', 'spam']
    assert not is_sorted(items)


@pytest.fixture
def readerr(capsys):
    """Supply a function that, when called, returns captured standard error."""
    return lambda: capsys.readouterr().err


@pytest.mark.parametrize('message, expected', [
    ("Wall is still up.", "alert: Wall is still up.\n"),
    ("in your base.", "alert: in your base.\n"),
    ("killing your dudes.", "alert: killing your dudes.\n"),
    ('refusing to say hello', 'alert: refusing to say hello\n'),
    ('3609 squirrels complained', 'alert: 3609 squirrels complained\n'),
    ('boycott whalebone skis', 'alert: boycott whalebone skis\n'),
])
def test_alert_and_newline_are_printed_with_string(readerr, message, expected):
    alert(message)
    assert readerr() == expected


def test_alert_with_nonstring_message_prints_str_of_message(readerr):
    alert(Fraction(2, 3))
    assert readerr() == 'alert: 2/3\n'


@pytest.mark.parametrize('value', [True, 1, 1.1, 'hello', object()])
def test_bail_if_bails_if_truthy(value):
    with pytest.raises(SystemExit) as exc_info:
        bail_if(value)
    assert exc_info.value.code == 1


@pytest.mark.parametrize('value', [False, 0, 0.0, '', None])
def test_bail_if_does_not_bail_if_falsy(value):
    try:
        bail_if(value)
    except SystemExit:
        pytest.fail('Bailed although condition was falsy.')


@pytest.mark.parametrize('implementation', [
    MulSquarer,
    PowSquarer,
    make_squarer,
])
class TestAllSquarers:
    """Tests for any kind of squarer."""

    __slots__ = ()

    @pytest.mark.parametrize('num, expected', [
        (0, 0),
        (1, 1),
        (2, 4),
        (3, 9),
    ])
    def test_positive_ints_are_squared(self, implementation, num, expected):
        squarer = implementation()
        assert squarer(num) == expected

    @pytest.mark.parametrize('num, expected', [
        (0.0, 0.0),
        (1.0, 1.0),
        (2.2, 4.84),
        (3.1, 9.61),
    ])
    def test_positive_floats_are_squared(self, implementation, num, expected):
        squarer = implementation()
        assert squarer(num) == pytest.approx(expected)

    @pytest.mark.parametrize('num, expected', [
        (-1, 1),
        (-2, 4),
        (-3, 9),
        (-4, 16),
    ])
    def test_negative_ints_are_squared(self, implementation, num, expected):
        squarer = implementation()
        assert squarer(num) == expected

    @pytest.mark.parametrize('num, expected', [
        (-1.2, 1.44),
        (-1.0, 1.0),
        (-2.2, 4.84),
        (-3.1, 9.61),
    ])
    def test_negative_floats_are_squared(self, implementation, num, expected):
        squarer = implementation()
        assert squarer(num) == pytest.approx(expected)


class TestSquarerClasses:
    """Tests for the custom Squarer classes."""

    __slots__ = ()

    @pytest.mark.parametrize('implementation, expected_repr', [
        (MulSquarer, 'MulSquarer()'),
        (PowSquarer, 'PowSquarer()'),
    ])
    def test_repr(self, implementation, expected_repr):
        """repr shows type and looks like Python code."""
        squarer = implementation()
        assert repr(squarer) == expected_repr

    @pytest.mark.parametrize('implementation', [MulSquarer, PowSquarer])
    def test_squarer_is_a_squarer(self, implementation):
        squarer = implementation()
        assert isinstance(squarer, Squarer)

    @pytest.mark.parametrize('implementation', [MulSquarer, PowSquarer])
    def test_squarers_of_same_type_are_equal(self, implementation):
        lhs = implementation()
        rhs = implementation()
        assert lhs == rhs

    @pytest.mark.parametrize('impl1, impl2', [
        (MulSquarer, PowSquarer),
        (PowSquarer, MulSquarer),
    ])
    def test_squarers_of_different_types_are_not_equal(self, impl1, impl2):
        lhs = impl1()
        rhs = impl2()
        assert lhs != rhs

    @pytest.mark.parametrize('implementation', [MulSquarer, PowSquarer])
    def test_squarers_of_same_type_hash_equal(self, implementation):
        lhs = implementation()
        rhs = implementation()
        assert hash(lhs) == hash(rhs)


if __name__ == '__main__':
    sys.exit(pytest.main())
