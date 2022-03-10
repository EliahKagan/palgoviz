#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall FILENAME [LANG]
"""

from multiprocessing.sharedctypes import Value
import sys

from greet import make_greeter


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


def greet_all(path, lang):
    """Greet all in a file given the path and language."""
    greeter = make_greeter(lang)
    with open(path, encoding='utf-8') as file:
        greet_names(file, greeter)


def greet_all_try(path, lang):
    """
    Greet all in a file given the path and language.

    Uses an explicit try-finally instead of a with statement.
    """
    greeter = make_greeter(lang)
    file = open(path, encoding='utf-8')
    try:
        greet_names(file, greeter)
    finally:
        file.close()


def run(name_reading_greeter):
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

    # Uses EAFP (easier to ask forgiveness than permission).
    try:
        name_reading_greeter(path, lang)
    except (OSError, ValueError) as error:
        # Something went wrong opening or reading (or closing) the file.
        perror(error)
        return 1
    return 0


if __name__ == '__main__':  # If we are running this module as a script.
    # For exit codes in powershell, $LASTEXITCODE.
    sys.exit(run(greet_all))
