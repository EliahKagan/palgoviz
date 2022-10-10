#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall FILENAME [LANG]

The filename must be passed, but the language code is optional.

Basic examples/tests:

    >>> from subprocess import getstatusoutput as gso

    >>> _, output = gso('python greetall.py ../data/names.txt en')
    >>> print(output)
    Hello, Eliah!
    Hello, David!
    Hello, Dr. Evil!

    >>> _, output = gso('python greetall.py ../data/names.txt es')
    >>> print(output)
    ¡Hola, Eliah!
    ¡Hola, David!
    ¡Hola, Dr. Evil!

See test_greetall.txt for more tests.
"""

__all__ = ['greet_all', 'greet_all_try', 'Config', 'run']

import sys

import attrs

import greet


def pmessage(prefix, message):
    """Print a message. Helper for perror and pwarn."""
    print(f'{prefix} in {sys.argv[0]}: {message}', file=sys.stderr)


def perror(message):
    """Print an error message."""
    pmessage('ERROR', message)


def pwarn(message):
    """Print a warning message."""
    pmessage('WARNING', message)


def greet_names(name_lines, greeter):
    """Greet each name in name_lines in given language."""
    greeted = set()
    for line in name_lines:
        name = line.strip()
        if name and name not in greeted:
            greeter(name)
            greeted.add(name)


def greet_all(path, greeter):
    """Greet all in a file given the path and language."""
    with open(path, encoding='utf-8') as file:
        greet_names(file, greeter)


def greet_all_try(path, greeter):
    """
    Greet all in a file given the path and language.

    Uses an explicit try-finally instead of a with statement.
    """
    file = open(path, encoding='utf-8')
    try:
        greet_names(file, greeter)
    finally:
        file.close()


@attrs.frozen
class Config:
    """
    Configuration specifying dependencies for the run function.

    >>> Config()  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Config(names_processor=<function greet_all at 0x...>,
           greeter_factory=<class 'greet.FrozenGreeter'>)
    >>> _ == Config(greet_all, greet.FrozenGreeter)
    True
    >>> Config() == Config(names_processor=greet_all_try)
    False
    >>> Config() == Config(greeter_factory=greet.MutableGreeter)
    False
    """
    names_processor = attrs.field(default=greet_all)
    greeter_factory = attrs.field(default=greet.FrozenGreeter)


def run(configuration):
    """Run the script."""
    # Uses LBYL (look before you leap).
    # block comments, (VSCODE) control + K + C, uncomment control + K + U
    match sys.argv:
        case [_]:
            perror('Did not pass a filename')
            return 1
        case [_, path]:
            lang = 'en'
        case [_, path, lang]:
            pass
        case [_, path, lang, *_]:
            pwarn('Too many arguments, see docstring for usage')

    try:
        greeter = configuration.greeter_factory(lang)
    except ValueError as error:
        perror(error)
        return 1

    # Uses EAFP (easier to ask forgiveness than permission).
    try:
        configuration.names_processor(path, greeter)
    except OSError as error:
        # Something went wrong opening or reading (or closing) the file.
        perror(error)
        return 1
    return 0


if __name__ == '__main__':  # If we are running this module as a script.
    # For exit codes in PowerShell, $LASTEXITCODE.
    sys.exit(run(Config()))
