#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall.py FILENAME [LANG]
"""

import sys

from algoviz import greet


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


class Config:
    """Configuration specifying dependencies for the run() function."""

    __slots__ = ('names_processor', 'greeter_factory')

    def __init__(self,
                 names_processor=greet_all,
                 greeter_factory=greet.FrozenGreeter):
        """Create a run configuration, optionally customizing dependencies."""
        self.names_processor = names_processor
        self.greeter_factory = greeter_factory


def run(configuration):
    """Run the script."""
    # Uses LBYL (look before you leap).
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
    # For exit codes in Bash, $?. For exit codes in PowerShell, $LASTEXITCODE.
    sys.exit(run(Config()))
