#!/usr/bin/env python

# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
pytest tests for the simple code in simple.py.

The purpose of this module is to introduce and practice techniques for writing
tests with the pytest module (augmented with the pytest-subtest package).

See also test_simple.py for similar tests using unittest, not pytest.
"""

from abc import ABC, abstractmethod
from fractions import Fraction
import operator
import sys

import pytest  # NOTE: Often we do NOT need this import to write pytest tests.

from palgoviz.simple import (
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
    return Widget('vast', 'mauve')  # Arrange.


class TestWidget:
    """Tests for the Widget class."""

    __slots__ = ()

    def test_size_attribute_has_size(self, widget):
        assert widget.size == 'vast'

    def test_color_attribute_has_color(self, widget):
        assert widget.color == 'mauve'

    def test_size_can_be_changed(self, widget):
        widget.size = 'just barely visible'
        assert widget.size == 'just barely visible'

    def test_color_can_be_changed(self, widget):
        widget.color = 'royal purple'  # Act.
        assert widget.color == 'royal purple'  # Assert.

    def test_new_attributes_cannot_be_added(self, widget):
        with pytest.raises(AttributeError):
            widget.favorite_desert = 'Sahara'


class TestAnswer:
    """Tests for the answer function."""

    __slots__ = ()

    def test_the_answer_is_42(self):
        assert answer() == 42

    def test_the_answer_is_an_int(self):
        assert isinstance(answer(), int)


class TestIsSorted:
    """Tests for the is_sorted function."""

    __slots__ = ()

    def test_empty_list_is_sorted(self):
        items = []
        assert is_sorted(items)

    def test_empty_generator_is_sorted(self):
        items = (x for x in ())
        assert is_sorted(items)

    def test_one_element_list_is_sorted(self):
        items = [76]
        assert is_sorted(items)

    def test_ascending_two_element_list_is_sorted(self):
        items = ['a', 'b']
        assert is_sorted(items)

    @pytest.mark.parametrize('_kind, items', [
        ('strings', ['b', 'a']),
        ('integers', [3, 2]),
    ])
    def test_descending_two_element_list_is_not_sorted(self, _kind, items):
        assert not is_sorted(items)

    @pytest.mark.parametrize('_kind, items', [
        ('strings', (x for x in ('b', 'a'))),
        ('integers', (x for x in (3, 2))),
    ])
    def test_descending_two_element_generator_is_not_sorted(self,
                                                            _kind, items):
        assert not is_sorted(items)

    def test_ascending_two_element_generator_is_sorted(self):
        items = (ch for ch in 'ab')
        assert is_sorted(items)

    def test_equal_two_element_list_is_sorted(self):
        items = ['a', 'a']
        assert is_sorted(items)

    def test_equal_two_element_generator_is_sorted(self):
        items = (ch for ch in 'aa')
        assert is_sorted(items)

    def test_sorted_short_by_nontrivial_list_is_sorted(self):
        items = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']
        assert is_sorted(items)

    def test_unsorted_short_but_nontrivial_list_is_unsorted(self):
        items = ['bar', 'eggs', 'foo', 'ham', 'foobar', 'quux', 'baz', 'spam']
        assert not is_sorted(items)


@pytest.fixture
def read_err(capsys):
    """Supply a function that, when called, returns captured standard error."""
    return lambda: capsys.readouterr().err


class TestAlert:
    """Tests for the alert function."""

    __slots__ = ()

    @pytest.mark.parametrize('message, expected', [
        ("Wall is still up.", "alert: Wall is still up.\n"),
        ("in your base.", "alert: in your base.\n"),
        ("killing your dudes.", "alert: killing your dudes.\n"),
        ('refusing to say hello', 'alert: refusing to say hello\n'),
        ('3609 squirrels complained', 'alert: 3609 squirrels complained\n'),
        ('boycott whalebone skis', 'alert: boycott whalebone skis\n'),
    ])
    def test_alert_and_newline_are_printed_with_string(self, read_err,
                                                       message, expected):
        alert(message)
        assert read_err() == expected

    def test_alert_with_nonstring_message_prints_str_of_message(self,
                                                                read_err):
        alert(Fraction(2, 3))
        assert read_err() == 'alert: 2/3\n'


class BailIf:
    """Tests for the bail_if function."""

    __slots__ = ()

    @pytest.mark.parametrize('value', [True, 1, 1.1, 'hello', object()])
    def test_bail_if_bails_if_truthy(self, value):
        with pytest.raises(SystemExit) as exc_info:
            bail_if(value)
        assert exc_info.value.code == 1

    @pytest.mark.parametrize('value', [False, 0, 0.0, '', None])
    def test_bail_if_does_not_bail_if_falsy(self, value):
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


class _BaseTestToggleAbstract(ABC):
    """Abstract class for tests for different kinds of toggle."""

    __slots__ = ()

    @property
    @abstractmethod
    def implementation(self):
        """The toggle factory implementation being tested."""

    def test_start_true_returns_true_on_first_call(self):
        tf = self.implementation(True)
        assert tf() is True

    def test_start_false_returns_false_on_first_call(self):
        ft = self.implementation(False)
        assert ft() is False

    def test_start_true_cycles_true_false(self, subtests):
        expected_results = [True, False] * 5
        tf = self.implementation(True)

        for call_number, expected in enumerate(expected_results, 1):
            with subtests.test(call=call_number):
                assert tf() is expected

    def test_start_false_cycles_false_true(self, subtests):
        expected_results = [False, True] * 5
        ft = self.implementation(False)

        for call_number, expected in enumerate(expected_results, 1):
            with subtests.test(call=call_number):
                assert ft() is expected

    @pytest.mark.parametrize('value',
                             [0, 1, 0.0, 1.1, '', 'j3j', None, object()])
    def test_raises_TypeError_if_nonbool_is_passed(self, value):
        with pytest.raises(TypeError):
            self.implementation(value)

    def test_separate_toggles_maintain_independent_state(self, subtests):
        tf1 = self.implementation(True)
        ft1 = self.implementation(False)

        with subtests.test(exist='tf1,ft1', toggle='tf1', changes=1):
            assert tf1() is True
        with subtests.test(exist='tf1,ft1', toggle='ft1', changes=1):
            assert ft1() is False
        with subtests.test(exist='tf1,ft1', toggle='tf1', changes=2):
            assert tf1() is False
        with subtests.test(exist='tf1,ft1', toggle='tf1', changes=3):
            assert tf1() is True
        with subtests.test(exist='tf1,ft1', toggle='ft1', changes=2):
            assert ft1() is True
        with subtests.test(exist='tf1,ft1', toggle='ft1', changes=3):
            assert ft1() is False

        ft2 = self.implementation(False)

        with subtests.test(exist='tf1,ft1,ft2', toggle='ft1', changes=4):
            assert ft1() is True
        with subtests.test(exist='tf1,ft1,ft2', toggle='ft2', changes=1):
            assert ft2() is False

        tf2 = self.implementation(True)

        with subtests.test(exist='tf1,ft1,ft2,tf2', toggle='tf2', changes=1):
            assert tf2() is True
        with subtests.test(exist='tf1,ft1,ft2,tf2', toggle='tf1', changes=4):
            assert tf1() is False
        with subtests.test(exist='tf1,ft1,ft2,tf2', toggle='ft2', changes=2):
            assert ft2() is True
        with subtests.test(exist='tf1,ft1,ft2,tf2', toggle='ft1', changes=5):
            assert ft1() is False


class TestMakeToggle(_BaseTestToggleAbstract):
    """Tests for the make_toggle function."""

    __slots__ = ()

    @property
    def implementation(self):
        return make_toggle


class TestMakeToggleAlt(_BaseTestToggleAbstract):
    """Tests for the make_toggle_alt function."""

    __slots__ = ()

    @property
    def implementation(self):
        return make_toggle_alt


class TestToggleClass(_BaseTestToggleAbstract):
    """Tests for the Toggle class."""

    __slots__ = ()

    @property
    def implementation(self):
        return Toggle

    def test_repr_true(self):
        """repr in True state shows True and looks like Python code."""
        tf = Toggle(True)
        assert repr(tf) == 'Toggle(True)'

    def test_repr_false(self):
        """repr in False state shows False and looks like Python code."""
        ft = Toggle(False)
        assert repr(ft) == 'Toggle(False)'

    @pytest.mark.parametrize('start, expected_results', [
        (True, ['Toggle(False)', 'Toggle(True)'] * 5),
        (False, ['Toggle(True)', 'Toggle(False)'] * 5),
    ])
    def test_repr_cycles(self, subtests, start, expected_results):
        """bool literal in repr changes with each call to the object."""
        toggle = Toggle(start)

        for call_number, expected in enumerate(expected_results, 1):
            with subtests.test(call=call_number):
                toggle()
                assert repr(toggle) == expected

    @pytest.mark.parametrize('start', [True, False])
    def test_toggle_objects_with_same_state_are_equal(self, start):
        assert Toggle(start) == Toggle(start)

    @pytest.mark.parametrize('lhs_start, rhs_start', [
        (True, False),
        (False, True),
    ])
    def test_toggle_objects_with_different_state_are_not_equal(self,
                                                               lhs_start,
                                                               rhs_start):
        assert Toggle(lhs_start) != Toggle(rhs_start)

    @pytest.mark.parametrize('calls, assertion', [
        (1, operator.eq),
        (2, operator.ne),
        (11, operator.eq),
        (12, operator.ne),
    ])
    def test_toggle_equality_is_correct_after_state_changes(self, subtests,
                                                            calls, assertion):
        fixed = Toggle(True)
        varying = Toggle(False)
        for _ in range(calls):
            varying()
        with subtests.test(compare='fixed,varying'):
            assert assertion(fixed, varying)
        with subtests.test(compare='varying,fixed'):
            assert assertion(varying, fixed)

    @pytest.mark.parametrize('start', [True, False])
    def test_hashing_toggle_raises_TypeError(self, start):
        toggle = Toggle(start)
        with pytest.raises(TypeError):
            hash(toggle)


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
