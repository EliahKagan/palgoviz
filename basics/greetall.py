#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall FILENAME [LANG]

TODO: Write better, more exhaustive tests, probably with pytest.

>>> from subprocess import getstatusoutput as gso
>>> status, output = gso('python greetall.py names.txt')
>>> status
0
>>> print(output)
Hello, Eliah!
Hello, David!
Hello, Dr. Evil!
>>> status, output = gso('python greetall.py names2.txt es')
>>> status
0
>>> print(output)
¡Hola, Eliah!
¡Hola, David!
¡Hola, Dr. Evil!
¡Hola, Stalin!
>>> status, output = gso('python greetall.py')
>>> status
1
>>> print(output)
ERROR in greetall.py: Did not pass a filename
>>> status, output = gso('python greetall.py names.txt qx')
>>> status
1
>>> print(output)
ERROR in greetall.py: Did not pass a valid language code
>>> status, output = gso('python greetall.py names.txt en foo')
>>> status
0
>>> print(output)
WARNING in greetall.py: Too many arguments, see docstring for usage
Hello, Eliah!
Hello, David!
Hello, Dr. Evil!
>>> status, output = gso('python greetall.py some-nonexistent-file.txt')
>>> status
1
>>> output.startswith('ERROR in greetall.py:')
True
>>> status, output = gso('python greetall.py .')
>>> status
1
>>> output.startswith('ERROR in greetall.py:')
True
"""

import sys

from greet import hello, FORMATS


def pmessage(prefix, message):
    """Print a message. Helper for perror and pwarn."""
    print(f'{prefix} in {sys.argv[0]}: {message}', file=sys.stderr)


def perror(message):
    """Print an error message."""
    pmessage('ERROR', message)


def pwarn(message):
    """Print a warning message."""
    pmessage('WARNING', message)


def greet_all(path, lang):
    """Greet all in a file given the path and language."""
    with open(path, encoding='utf-8') as file:
        names = set()
        for line in file:
            name = line.strip()
            if name and name not in names:
                hello(name, lang)
                names.add(name)


def greet_all_try(path, lang):
    """
    Greet all in a file given the path and language.

    Uses an explicit try-finally instead of a with statement.
    """
    file = open(path, encoding='utf-8')
    try:
        names = set()
        for line in file:
            name = line.strip()
            if name and name not in names:
                hello(name, lang)
                names.add(name)
    finally:
        file.close()


def run():
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

    if lang not in FORMATS:
        perror('Did not pass a valid language code')
        return 1

    # Uses EAFP (easier to ask forgiveness than permission).
    try:
        greet_all_try(path, lang)
    except OSError as error:
        # Something went wrong opening or reading (or closing) the file.
        perror(error)
        return 1
    return 0


if __name__ == '__main__':  # If we are running this module as a script.
    sys.exit(run()) # for exit codes in powershell, $LASTEXITCODE
