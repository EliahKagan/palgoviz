#!/usr/bin/env python

"""Tests for greetall.py."""

from typing import Protocol, NamedTuple

from pytest import CaptureFixture, MonkeyPatch, fixture

from greetall import run


class Result(NamedTuple):
    status: int
    out: str
    err: str


class Invoker(Protocol):
    def __call__(self, *__args: str) -> Result: ...


@fixture
def invoke(capsys: CaptureFixture, monkeypatch: MonkeyPatch) -> Invoker:
    def invoker(*args: str) -> Result:
        monkeypatch.setattr('sys.argv', ['PROGNAME', *args])
        status = run()
        outerr = capsys.readouterr()
        return Result(status, outerr.out, outerr.err)

    return invoker


def test_no_arguments_is_error(invoke: Invoker) -> None:
    """Passing no filename prints an error and bails."""
    status, out, err = invoke()
    assert status == 1
    assert out == ''
    assert err == 'ERROR in PROGNAME: Did not pass a filename\n'


def test_warns_on_multiple_arguments(invoke: Invoker) -> None:
    """Passing multiple command-line arguments warns and continues."""
    status, _, err = invoke('names.txt', 'other-arg')
    assert status == 0, "Extra arguments don't cause failure status."
    assert err == ('WARNING in PROGNAME: '
                   'Too many arguments, see doctring for usage\n')


def test_nonexistent_file_is_error(invoke: Invoker) -> None:
    """Naming a nonexistent file prints an error and bails."""
    status, out, err = invoke('nonexistent-file')
    assert status == 1
    assert out == ''
    assert err == ("ERROR in PROGNAME: "
                   "[Errno 2] No such file or directory: 'nonexistent-file'\n")


def test_directory_is_error(invoke: Invoker) -> None:
    """Naming a directory instead of a file prints an error and bails."""
    status, out, err = invoke('.')
    assert status == 1
    assert out == ''
    assert err.startswith('ERROR in PROGNAME: ')


def test_greets_names_txt_entries_correctly(invoke: Invoker) -> None:
    """Running on the test file names.txt produces the expected output."""
    status, out, err = invoke('names.txt')
    assert status == 0
    assert out == 'Hello, Eliah!\nHello, David!\nHello, Dr. Evil!\n'
    assert err == ''
