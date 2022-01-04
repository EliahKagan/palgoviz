#!/usr/bin/env python

"""Tests for greetall.py."""

from pytest import CaptureFixture, MonkeyPatch

from greetall import run


def test_no_arguments_is_error(capsys: CaptureFixture,
                               monkeypatch: MonkeyPatch) -> None:
    """Passing no filename prints an error and bails."""
    monkeypatch.setattr('sys.argv', ['PROGNAME'])
    status = run()
    message = capsys.readouterr().err
    assert status == 1
    assert message == 'ERROR in PROGNAME: Did not pass a filename\n'


def test_warns_on_multiple_arguments(capsys: CaptureFixture,
                                     monkeypatch: MonkeyPatch) -> None:
    """Passing multiple command-line arguments warns and continues."""
    monkeypatch.setattr('sys.argv', ['PROGNAME', 'names.txt', 'other-arg'])
    status = run()
    message = capsys.readouterr().err
    assert status == 0, "Extra arguments don't cause failure status."
    assert (message == 'WARNING in PROGNAME:'
                       ' Too many arguments, see doctring for usage\n')


def test_nonexistent_file_is_error(capsys: CaptureFixture,
                                   monkeypatch: MonkeyPatch) -> None:
    """Naming a nonexistent file prints an error and bails."""
    monkeypatch.setattr('sys.argv', ['PROGNAME', 'nonexistent-file'])
    status = run()
    message = capsys.readouterr().err
    assert status == 1
    assert (message ==
            "ERROR in PROGNAME:"
            " [Errno 2] No such file or directory: 'nonexistent-file'\n")


def test_directory_is_error(capsys: CaptureFixture,
                            monkeypatch: MonkeyPatch) -> None:
    """Naming a directory instead of a file prints an error and bails."""
    monkeypatch.setattr('sys.argv', ['PROGNAME', '.'])
    status = run()
    message = capsys.readouterr().err
    assert status == 1
    assert message.startswith('ERROR in PROGNAME: ')
