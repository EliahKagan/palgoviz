#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall FILENAME [LANG]
"""

import sys

from greet import hello, FORMATS


def perror(message):
    print(f'ERROR in {sys.argv[0]}: {message}', file=sys.stderr)
    

def pwarn(message):
    print(f'WARNING in {sys.argv[0]}: {message}', file=sys.stderr)


def run():
    """Run the script."""
    # Uses LBYL (look before you leap).
    # block comments, (VSCODE) control + K + C, uncomment control + K + U
    match sys.argv:
        case (command,):
            perror('Did not a pass filename')
            return 1
        case (command, name):
            lang = 'en'
        case (command, name, lang):
            pass             
        case (command, name, lang, *_):
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
