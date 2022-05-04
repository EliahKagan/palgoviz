#!/usr/bin/env python

"""
pytest tests for the simple code in simple.py.

The purpose of this module is to introduce and practice techniques for writing
tests with the pytest module (augmented with the pytest-subtest package).

See also test_simple.py for similar tests using unittest, not pytest.
"""

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


if __name__ == '__main__':
    sys.exit(pytest.main())
