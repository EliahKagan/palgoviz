#!/usr/bin/env python

"""
Tests for greetall.py.

Tests for the full functionality of greetall.py should go here eventually. For
now, see test_greetall.txt. Currently this only has tests for the Config class.
"""

import itertools
import unittest

from parameterized import parameterized

import greet
import greetall


_NAMES_PROCESSORS = [greetall.greet_all, greetall.greet_all_try]
"""Values to test for the names_processor attribute."""

_GREETER_FACTORIES = [greet.FrozenGreeter, greet.MutableGreeter]
"""Values to test for the greeter_factory attribute."""

_parameterize_by_names_processor = parameterized.expand([
    (func.__name__, func) for func in _NAMES_PROCESSORS
])
"""Parameterize a test method by names_processor attribute values."""

_parameterize_by_greeter_factory = parameterized.expand([
    (cls.__name__, cls) for cls in _GREETER_FACTORIES
])
"""Parameterize a test method by greeter_factory attribute values."""

_parameterize_by_names_processor_and_greeter_factory = parameterized.expand([
    (f'{func.__name__}_{cls.__name__}', func, cls)
    for func in _NAMES_PROCESSORS for cls in _GREETER_FACTORIES
])
"""Parameterize a test method by both names_processor and greeter_factory."""


class TestConfig(unittest.TestCase):
    """Tests for the Config class."""

    def test_defaults(self):
        """The defaults are greet_all and FrozenGreeter."""
        config = greetall.Config()
        with self.subTest('names_processor'):
            self.assertIs(config.names_processor, greetall.greet_all)
        with self.subTest('greeter_factory'):
            self.assertIs(config.greeter_factory, greet.FrozenGreeter)

    @_parameterize_by_names_processor
    def test_custom_names_processor(self, _label, names_processor):
        """If passed by itself, names_processor is used with FrozenGreeter."""
        config = greetall.Config(names_processor=names_processor)
        with self.subTest('names_processor'):
            self.assertIs(config.names_processor, names_processor)
        with self.subTest('greeter_factory'):
            self.assertIs(config.greeter_factory, greet.FrozenGreeter)

    @_parameterize_by_greeter_factory
    def test_custom_greeter_factory(self, _label, greeter_factory):
        """If passed by itself, greeter_factory is used with greet_all."""
        config = greetall.Config(greeter_factory=greeter_factory)
        with self.subTest('names_processor'):
            self.assertIs(config.names_processor, greetall.greet_all)
        with self.subTest('greeter_factory'):
            self.assertIs(config.greeter_factory, greeter_factory)

    @_parameterize_by_names_processor_and_greeter_factory
    def test_custom_names_processor_and_greeter_factory(self, _label,
                                                        names_processor,
                                                        greeter_factory):
        """Both names_processor and greeter_factory are used if passed."""
        config = greetall.Config(names_processor=names_processor,
                                 greeter_factory=greeter_factory)
        with self.subTest('names_processor'):
            self.assertIs(config.names_processor, names_processor)
        with self.subTest('greeter_factory'):
            self.assertIs(config.greeter_factory, greeter_factory)


if __name__ == '__main__':
    unittest.main()
