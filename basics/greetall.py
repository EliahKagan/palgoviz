#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall FILENAME [LANG]
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


def run():
    """Run the script."""
    # Uses LBYL (look before you leap).
    # block comments, (VSCODE) control + K + C, uncomment control + K + U
    match sys.argv:
        case [_]:
            perror('Did not pass a filename')
            return 1
        case [_, name]:
            lang = 'en'
        case [_, name, lang]:
            pass
        case [_, name, lang, *_]:
            pwarn('Too many arguments, see doctring for usage')

    if lang not in FORMATS:
        perror('Did not pass a valid language code')
        return 1

    # Uses EAFP (easier to ask forgiveness than permission).
    try:
        with open(name, encoding='utf-8') as file: 
            for line in file:
                hello(line.strip(), lang) 
    except OSError as error:
        # Something went wrong opening or reading (or closing) the file.
        perror(error)
        return 1
    return 0 


if __name__ == '__main__':  # If we are running this module as a script.
    sys.exit(run()) # for exit codes in powershell, $LASTEXITCODE
