#!/usr/bin/env python

"""Tests for greetall.py."""

import os
import sys
from typing import Any, NamedTuple, Protocol, runtime_checkable

import pytest
from typeguard import typechecked

from algoviz import greet, greetall


def _data_file_path(filename: str) -> str:
    """Get the path to a data file."""
    return os.path.join(os.path.dirname(__file__), '..', 'data', filename)


_NAMES = _data_file_path('names.txt')

_NAMES2 = _data_file_path('names2.txt')


@typechecked
class Result(NamedTuple):
    """Data representing the effects of running greetall.run()."""
    status: int
    out: str
    err: str


@runtime_checkable
class Invoker(Protocol):  # pylint: disable=too-few-public-methods
    """Interface for invokers. See invoke()."""
    def __call__(self, *__args: str) -> Result: ...


@pytest.fixture(name='names_processor',
                params=[greetall.greet_all, greetall.greet_all_try])
def fixture_names_processor(request: Any):
    return request.param


@pytest.fixture(name='greeter_factory',
                params=[greet.MutableGreeter, greet.FrozenGreeter])
def fixture_greeter_factory(request: Any):
    return request.param


@pytest.fixture(name='invoke')
@typechecked
def fixture_invoke(capsys: pytest.CaptureFixture,
                   monkeypatch: pytest.MonkeyPatch,
                   names_processor: Any,
                   greeter_factory: Any) -> Invoker:
    """Helper to return a function that automates input and output."""
    def invoker(*args: str) -> Result:
        monkeypatch.setattr('sys.argv', ['PROGNAME', *args])
        config = greetall.Config(names_processor, greeter_factory)
        status = greetall.run(config)
        outerr = capsys.readouterr()
        return Result(status, outerr.out, outerr.err)

    return invoker


@typechecked
def test_no_arguments_is_error(invoke: Invoker) -> None:
    """Passing no filename prints an error and bails."""
    status, out, err = invoke()
    assert status == 1
    assert out == ''
    assert err == 'ERROR in PROGNAME: Did not pass a filename\n'


@typechecked
def test_nonexistent_file_is_error(invoke: Invoker) -> None:
    """Naming a nonexistent file prints an error and bails."""
    status, out, err = invoke('nonexistent-file')
    assert status == 1
    assert out == ''
    assert err == ("ERROR in PROGNAME: "
                   "[Errno 2] No such file or directory: 'nonexistent-file'\n")


@typechecked
def test_directory_is_error(invoke: Invoker) -> None:
    """Naming a directory instead of a file prints an error and bails."""
    status, out, err = invoke('.')
    assert status == 1
    assert out == ''
    assert err.startswith('ERROR in PROGNAME: ')


@typechecked
def test_greets_from_simple_file(invoke: Invoker) -> None:
    """Greets without duplicates and extra whitespace (implicit English)."""
    status, out, err = invoke(_NAMES)
    assert status == 0
    assert out == 'Hello, Eliah!\nHello, David!\nHello, Dr. Evil!\n'
    assert err == ''


@typechecked
def test_greets_from_simple_file_lang_en(invoke: Invoker) -> None:
    """Greets without duplicates and extra whitespace, in English."""
    status, out, err = invoke(_NAMES, 'en')
    assert status == 0
    assert out == 'Hello, Eliah!\nHello, David!\nHello, Dr. Evil!\n'
    assert err == ''


@typechecked
def test_greets_from_simple_file_lang_es(invoke: Invoker) -> None:
    """Greets without duplicates and extra extra whitespace, in Spanish."""
    status, out, err = invoke(_NAMES, 'es')
    assert status == 0
    assert out == '¡Hola, Eliah!\n¡Hola, David!\n¡Hola, Dr. Evil!\n'
    assert err == ''


@typechecked
def test_greets_from_file_with_dupes_and_ws(invoke: Invoker) -> None:
    """Greets, ignoring extra whitespace and duplicates (implicit English)."""
    status, out, err = invoke(_NAMES2)
    assert status == 0
    assert out == ('Hello, Eliah!\nHello, David!\nHello, Dr. Evil!\n'
                   'Hello, Stalin!\n')
    assert err == ''


@typechecked
def test_greets_from_file_with_dupes_and_ws_lang_en(invoke: Invoker) -> None:
    """Greets, ignoring extra whitespace and duplicates, in English."""
    status, out, err = invoke(_NAMES2, 'en')
    assert status == 0
    assert out == ('Hello, Eliah!\nHello, David!\nHello, Dr. Evil!\n'
                   'Hello, Stalin!\n')
    assert err == ''


@typechecked
def test_greets_from_file_with_dupes_and_ws_lang_es(invoke: Invoker) -> None:
    """Greets, ignoring extra whitespace and duplicates, in Spanish."""
    status, out, err = invoke(_NAMES2, 'es')
    assert status == 0
    assert out == ('¡Hola, Eliah!\n¡Hola, David!\n¡Hola, Dr. Evil!\n'
                   '¡Hola, Stalin!\n')
    assert err == ''


# @typechecked
# def test_greets_from_file_with_dupes(and_ws )


@typechecked
def test_warns_on_extra_arg_without_error(invoke: Invoker) -> None:
    """Passing an extra command-line argument warns and continues."""
    status, _, err = invoke(_NAMES, 'en', 'other-arg')
    assert status == 0, "Extra arguments don't cause failure status."
    assert err == ('WARNING in PROGNAME: '
                   'Too many arguments, see docstring for usage\n')


@typechecked
def test_warns_on_multiple_extra_args_without_error(invoke: Invoker) -> None:
    """Passing multiple extra command-line arguments warns and continues."""
    status, _, err = invoke(_NAMES, 'es', 'other1', 'other2', 'other3')
    assert status == 0, "Extra arguments don't cause failure status."
    assert err == ('WARNING in PROGNAME: '
                   'Too many arguments, see docstring for usage\n')


# @typechecked
# def test_warns_on_extra_arg_with_error(invoke: Invoker) -> None:
#     """Passing a """


if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
